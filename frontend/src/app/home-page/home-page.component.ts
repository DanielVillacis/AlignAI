import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { MatDatepickerModule} from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { provideNativeDateAdapter } from '@angular/material/core';
import { NgxChartsModule, LegendPosition } from '@swimlane/ngx-charts';
import * as shape from 'd3-shape';
import { group } from '@angular/animations';
import { NgApexchartsModule } from 'ng-apexcharts';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { CreateEventFormComponent } from '../create-event-form/create-event-form.component';


import {
  ApexChart,
  ApexAxisChartSeries,
  ApexStroke,
  ApexDataLabels,
  ApexXAxis,
  ApexYAxis,
  ApexLegend,
  ApexFill,
  ApexTooltip,
  ApexGrid
} from 'ng-apexcharts';

// Define chart options type
export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  stroke: ApexStroke;
  dataLabels: ApexDataLabels;
  yaxis: ApexYAxis;
  colors: string[];
  labels: string[];
  legend: ApexLegend;
  fill: ApexFill;
  tooltip: ApexTooltip;
  grid: ApexGrid;
};


@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule, 
    MatDatepickerModule, 
    MatNativeDateModule,
    NgApexchartsModule,
    ReactiveFormsModule,
    MatDialogModule
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

  // ------------- Apex Chart -------------
  // ApexCharts configuration
  series: ApexAxisChartSeries = [];
  chart: ApexChart = {
    height: 300,
    type: 'area',
    toolbar: {
      show: false
    },
    zoom: {
      enabled: false
    }
  };
  dataLabels: ApexDataLabels = {
    enabled: false
  };
  stroke: ApexStroke = {
    curve: 'smooth',
    width: 2
  };
  xaxis: ApexXAxis = {
    type: 'category',
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    tickPlacement: 'on'
  };
  yaxis: ApexYAxis = {
    title: {
      text: '',
    },
    labels: {
      show: false
    },
    axisTicks: {
      show: false
    },
    axisBorder: {
      show: false
    }
  };
  colors: string[] = ['#3EC9B9', '#303545'];
  legend: ApexLegend = {
    position: 'bottom'
  };
  fill: ApexFill = {
    type: 'gradient',
    gradient: {
      shadeIntensity: 0.5,
      opacityFrom: 0.6,
      opacityTo: 0.3,
      stops: [40, 90, 100]
    }
  };
  labels: string[] = [];

  grid: ApexGrid = {
    show: true,
    borderColor: 'transparent',
    xaxis: {
      lines: {
        show: false // Hide vertical grid lines
      }
    },
    yaxis: {
      lines: {
        show: false // Hide horizontal grid lines
      }
    },
    padding: {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    }
  };



  constructor(
    private http: HttpClient, 
    private fb: FormBuilder,
    private dialog: MatDialog) {
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
    this.generateChartData();
    this.getClients(); // Fetch clients for dropdown
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
    
    this.http.get<any[]>(`http://127.0.0.1:5000/api/events?date=${formattedDate}`)
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
    this.http.get<any[]>('http://127.0.0.1:5000/api/clients')
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

  // Replace toggleEventForm with this method
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
        
        this.http.post('http://127.0.0.1:5000/api/events', eventData)
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

  // Create new event
  createEvent() {
    if (this.eventForm.valid) {
      const eventData = this.eventForm.value;
      
      // Ensure date is in correct format
      if (this.selectedDate) {
        eventData.event_date = this.formatDateForApi(this.selectedDate) + 'T' + 
                              (eventData.event_time || '09:00:00');
      }
      
      this.http.post('http://127.0.0.1:5000/api/events', eventData)
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

  // Delete event
  deleteEvent(eventId: number) {
    if (confirm('Are you sure you want to delete this event?')) {
      this.http.delete(`http://127.0.0.1:5000/api/events/${eventId}`)
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
    this.http.get<any[]>('http://127.0.0.1:5000/api/scans')
      .subscribe({
        next: (data) => {
          this.scans = data;
          this.generateChartData(); // for updating the chart when the data is fetched
        },
        error: (error) => {
          console.error('There was an error!', error);
        }
      }
      );
  }

  generateChartData() {
    // Sample data for the chart
    this.series = [
      {
        name: 'New Patients',
        data: [31, 40, 28, 51, 42, 109, 100, 50, 60, 70, 80, 90]
      },
      {
        name: 'Returning Patients',
        data: [11, 32, 45, 32, 34, 52, 41, 21, 31, 41, 51, 61]
      }
    ];
  }

}
