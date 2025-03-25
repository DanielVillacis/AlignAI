import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDatepickerModule} from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { provideNativeDateAdapter } from '@angular/material/core';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { CreateEventFormComponent } from '../create-event-form/create-event-form.component';
import { OverviewChartComponent } from '../overview-chart/overview-chart.component';
import { ClientService } from '../../services/client.service';
import { EventService } from '../../services/event.service';
import { ScanService } from '../../services/scan.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule, 
    MatDatepickerModule, 
    MatNativeDateModule,
    ReactiveFormsModule,
    MatDialogModule,
    OverviewChartComponent
  ],
  providers: [provideNativeDateAdapter()],
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.scss'],
})
export class HomePageComponent implements OnInit {
  selectedDate: Date | null = null;
  scheduledEvents: any[] = [];
  scans: any[] = [];
  isLoading: boolean = false;
  eventForm: FormGroup;
  showEventForm: boolean = false;
  clients: any[] = [];

  constructor(
    private fb: FormBuilder,
    private dialog: MatDialog,
    private clientService: ClientService,
    private eventService: EventService,
    private scanService: ScanService
  ) {
    // Initialize form
    this.eventForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      event_date: ['09:00', Validators.required],
      client_id: [null],
      is_scan: [false]
    });
  }

  ngOnInit(): void {
    this.getScans();
    this.getClients();
  }

  onDateSelected(date: Date) {
    this.selectedDate = date;
    this.getEventsForDate(date);
  
    // Update form with selected date
    if (this.eventForm) {
      this.eventForm.patchValue({
        event_date: this.formatDateForApi(date)
      });
    }
  }

  getEventsForDate(date: Date) {
    this.isLoading = true;
    const formattedDate = this.formatDateForApi(date);
    
    this.eventService.getEventsForDate(formattedDate)
      .subscribe({
        next: (data) => {
          this.scheduledEvents = data;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error fetching events:', error);
          this.isLoading = false;
        }
      });
  }

  getClients() {
    this.clientService.getClients()
      .subscribe({
        next: (data) => {
          this.clients = data;
        },
        error: (error) => {
          console.error('Error fetching clients:', error);
        }
      });
  }

  // Helper to format date for API
  formatDateForApi(date: Date): string {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  openEventDialog(): void {
    const dialogRef = this.dialog.open(CreateEventFormComponent, {
      width: '500px',
      data: { 
        title: 'Add Event',
        clients: this.clients,
        selectedDate: this.selectedDate
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Create event with the form data
        const eventData = { ...result };
        
        // Ensure date is in correct format
        if (this.selectedDate) {
          const timeZoneOffset = new Date().getTimezoneOffset();
          const dateWithOffset = new Date(this.selectedDate.getTime() - timeZoneOffset * 60000);
          eventData.event_date = this.formatDateForApi(dateWithOffset) + 'T' + 
                              (eventData.event_time || '09:00:00') + 'Z';
        }
        
        this.eventService.createEvent(eventData)
          .subscribe({
            next: (response) => {
              console.log('Event created successfully', response);
              this.getEventsForDate(this.selectedDate!);
            },
            error: (error) => {
              console.error('Error creating event:', error);
            }
          });
      }
    });
  }

  createEvent() {
    if (this.eventForm.valid) {
      const eventData = this.eventForm.value;
      
      // Ensure date is in correct format
      if (this.selectedDate) {
        eventData.event_date = this.formatDateForApi(this.selectedDate) + 'T' + 
                              (eventData.event_time || '09:00:00');
      }
      
      this.eventService.createEvent(eventData)
        .subscribe({
          next: (response) => {
            console.log('Event created successfully', response);
            this.getEventsForDate(this.selectedDate!);
            this.eventForm.reset();
            this.showEventForm = false;
          },
          error: (error) => {
            console.error('Error creating event:', error);
          }
        });
    }
  }

  deleteEvent(eventId: number) {
    if (confirm('Are you sure you want to delete this event?')) {
      this.eventService.deleteEvent(eventId)
        .subscribe({
          next: () => {
            this.getEventsForDate(this.selectedDate!);
          },
          error: (error) => {
            console.error('Error deleting event:', error);
          }
        });
    }
  }

  getScans() {
    this.scanService.getScans()
      .subscribe({
        next: (data) => {
          this.scans = data;
        },
        error: (error) => {
          console.error('There was an error!', error);
        }
      });
  }
}
