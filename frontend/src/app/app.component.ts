import { Component } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { HttpClient, provideHttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [],
  template: `
    <h1>Welcome to the App!</h1>
    <button (click)="executeScript()">Run Python Script</button>
  `,
})
export class AppComponent {
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

bootstrapApplication(AppComponent, {
  providers: [provideHttpClient()],
});
