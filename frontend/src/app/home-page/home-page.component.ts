import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { MatDatepickerModule} from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { provideNativeDateAdapter } from '@angular/material/core';


@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, MatDatepickerModule, MatNativeDateModule],
  providers: [provideNativeDateAdapter()],
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.scss'],
})

export class HomePageComponent implements OnInit {
  selectedDate: Date | null = null;
  scheduledEvents: any[] = [];
  clients: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.getClients();
  }

  onDateSelected(date: Date) {
    this.selectedDate = date;
    // Here you would fetch events for the selected date
    // this.getEventsForDate(date);
  }

  getClients() {
    this.http.get<any[]>('http://127.0.0.1:5000/api/clients')
      .subscribe({
        next: (data) => {
          this.clients = data;
        },
        error: (error) => {
          console.error('There was an error!', error);
        }
      }
      );
  }
}
