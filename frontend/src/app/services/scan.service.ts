import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ScanService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getScans(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/scans`);
  }

  launchScan(): Observable<any> {
    return this.http.get(`${this.apiUrl}/run-script`);
  }

  getScanById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/scans/${id}`);
  }
} 