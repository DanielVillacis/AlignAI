import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';


@Component({
  selector: 'app-event-form-dialog',
  standalone: true,
  imports: [
    CommonModule, 
    ReactiveFormsModule, 
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule
  ],
  templateUrl: './create-event-form.component.html',
  styleUrls: ['./create-event-form.component.scss']
})


export class CreateEventFormComponent {
  eventForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<CreateEventFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.eventForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      event_time: ['09:00'],
      client_id: [null],
      is_scan: [false]
    });

    // If there's existing event data, populate the form
    if (data.event) {
      this.eventForm.patchValue(data.event);
    }
  }

  onSubmit(): void {
    if (this.eventForm.valid) {
      this.dialogRef.close(this.eventForm.value);
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
