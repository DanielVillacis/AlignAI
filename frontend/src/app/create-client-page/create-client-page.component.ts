import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { Router } from '@angular/router';

@Component({
  selector: 'app-create-client-page',
  standalone: true,
  imports: [ReactiveFormsModule, MatSnackBarModule],
  templateUrl: './create-client-page.component.html',
  styleUrl: './create-client-page.component.scss'
})
export class CreateClientPageComponent {
  clientForm: FormGroup;

  constructor(
    private fb: FormBuilder, 
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private router: Router) {
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

  addPatient() {
    if (this.clientForm.valid) {
      this.http.post('http://127.0.0.1:5000/api/clients', this.clientForm.value)
      .subscribe({
        next: (data) => {
          this.snackBar.open('Patient added successfully', 'Close', {
            duration: 5000,
            horizontalPosition: 'right',
            verticalPosition: 'bottom',
            panelClass: ['success-snackbar']
          });
          this.router.navigate(['/clients']);
          console.log('Patient added successfully', data);
        },
        error: (error) => {
          this.snackBar.open('Error adding patient', 'Close', {
            duration: 5000,
            horizontalPosition: 'right',
            verticalPosition: 'bottom',
            panelClass: ['error-snackbar']
          });
          console.error('Error adding patient', error);
        }});
    }
  }
}
