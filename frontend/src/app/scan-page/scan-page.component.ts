import { Component } from '@angular/core';
import { HttpClient, provideHttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'scan-page',
  standalone: true,
  imports: [HttpClientModule],
  templateUrl: './scan-page.component.html',
  styleUrls: ['./scan-page.component.scss'],
})

export class ScanPageComponent {
  constructor(private http: HttpClient) {}

  executeScript() {
    this.http.get('http://127.0.0.1:5000/run-script').subscribe(
      response => {
        console.log('Script executed:', response);
      },
      error => {
        console.error('Error executing script:', error);
      }
    );
  }
}
