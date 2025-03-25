import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ClientService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getClients(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/clients`);
  }

  getClientById(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/clients/${id}`);
  }

  createClient(clientData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/clients`, clientData);
  }

  updateClient(id: number, clientData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/clients/${id}`, clientData);
  }

  deleteClient(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/clients/${id}`);
  }
} 