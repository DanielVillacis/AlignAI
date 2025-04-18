import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { environment } from '../../environments/environment.local';
import { catchError, map } from 'rxjs/operators';


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

  checkLatestScanStatus(clientId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/scans/status/${clientId}/latest`);
  }

  downloadScanReport(scanId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/scans/download-report/${scanId}`, {
      responseType: 'blob',
      observe: 'response' 
    }).pipe(
      map(response => {
        // check if we got a PDF response (application/pdf)
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/pdf')) {
          return response.body as Blob;
        } else {
          // handle case where server returns error (might be JSON)
          throw new Error('Invalid response type, expected PDF');
        }
      }),
      catchError((error: unknown) => {
        console.error('PDF download error:', error);
        // convert error to readable format
        if (error instanceof HttpErrorResponse) {
          // using throwError instead of returning a promise
          return throwError(() => new Error(error.message || 'Error downloading report'));
        }
        return throwError(() => new Error('Error downloading report'));
      })
    );
  }
} 