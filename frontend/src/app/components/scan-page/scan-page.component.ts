import { Component } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ScanService } from '../../services/scan.service';

@Component({
  selector: 'scan-page',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './scan-page.component.html',
  styleUrls: ['./scan-page.component.scss'],
})

export class ScanPageComponent {
  clientForm: FormGroup;

  constructor(
    private fb: FormBuilder, 
    private scanService: ScanService
  ) {
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

  launchScan() {
    this.scanService.launchScan().subscribe({
      next: (data) => {
        console.log('Scan launched successfully', data);
      },
      error: (error) => {
        console.error('Error launching scan', error);
      }
    });
  }
}
