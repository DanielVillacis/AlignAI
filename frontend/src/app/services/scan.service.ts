import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.local';

@Injectable({
  providedIn: 'root'
})
export class ScanService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getScans(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/scans`);
  }

  launchScan(clientId: number, scanReason: string): Observable<any> {
    console.log(`Launching scan for client ${clientId} with reason  ${scanReason}`)
    return this.http.post(`${this.apiUrl}/ai/run-script`, {
      client_id: clientId,
      scan_reason: scanReason
    });
  }

  getScanById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/scans/${id}`);
  }
} 