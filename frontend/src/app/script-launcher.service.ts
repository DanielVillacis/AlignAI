import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ScriptLauncherService {

  private apiUrl = 'http://127.0.0.1:5000//run-script'; // Flask API endpoint

  constructor(private http: HttpClient) {}

  runScript(): Observable<any> {
    return this.http.get(this.apiUrl);
  }
}