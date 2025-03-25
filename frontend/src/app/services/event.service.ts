import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class EventService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getEventsForDate(date: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/events?date=${date}`);
  }

  createEvent(eventData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/events`, eventData);
  }

  deleteEvent(eventId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/events/${eventId}`);
  }
} 