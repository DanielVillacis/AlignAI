import { Component } from '@angular/core';
import { HttpClient, provideHttpClient, HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'scan-page',
  standalone: true,
  imports: [HttpClientModule, ReactiveFormsModule],
  templateUrl: './scan-page.component.html',
  styleUrls: ['./scan-page.component.scss'],
})

export class ScanPageComponent {
  clientForm: FormGroup;

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.clientForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      age: ['', Validators.required],
      gender: ['', Validators.required],
      telephone: ['', Validators.required],
      email: ['', Validators.required],
      reason: ['', Validators.required],
      previous_conditions: [''],
    });
  }

  // onSubmit() {
  //   if (this.clientForm.valid) {
  //     this.http.post('http://127.0.0.1:5000/api/clients', this.clientForm.value)
  //     .subscribe(
  //         response => console.log('Client added:', response),
  //         error => console.error('Error creating client:', error)
  //     );
  //   }
  // }

  // executeScript() {
  //   this.http.get('http://127.0.0.1:5000/run-script').subscribe(
  //     response => {
  //       console.log('Script executed:', response);
  //     },
  //     error => {
  //       console.error('Error executing script:', error);
  //     }
  //   );
  // }

  executeScript() {
    if (this.clientForm.valid) {
      // First create client
      this.http.post('http://127.0.0.1:5000/api/clients', this.clientForm.value)
        .subscribe(
          response => {
            console.log('Client added:', response);
            // Then run scan script
            this.http.get('http://127.0.0.1:5000/run-script').subscribe(
              response => {
                console.log('Script executed:', response);
              },
              error => {
                console.error('Error executing script:', error);
              }
            );
          },
          error => console.error('Error creating client:', error)
        );
    } else {
      console.error('Form is invalid');
    }
  }
}
