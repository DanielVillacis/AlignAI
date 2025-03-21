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
  template: `
    <h2 mat-dialog-title>{{data.title}}</h2>
    <mat-dialog-content>
      <form [formGroup]="eventForm">
        <div class="form-group">
          <mat-form-field appearance="outline" style="width: 100%;">
            <mat-label>Title</mat-label>
            <input matInput formControlName="title" placeholder="Event title">
          </mat-form-field>
        </div>
        
        <div class="form-group">
          <mat-form-field appearance="outline" style="width: 100%;">
            <mat-label>Description</mat-label>
            <textarea matInput formControlName="description" placeholder="Event description" rows="3"></textarea>
          </mat-form-field>
        </div>
        
        <div class="form-group">
          <mat-form-field appearance="outline" style="width: 100%;">
            <mat-label>Time</mat-label>
            <input matInput type="time" formControlName="event_time">
          </mat-form-field>
        </div>
        
        <div class="form-group">
          <mat-form-field appearance="outline" style="width: 100%;">
            <mat-label>Patient (Optional)</mat-label>
            <mat-select formControlName="client_id">
              <mat-option [value]="null">None</mat-option>
              <mat-option *ngFor="let client of data.clients" [value]="client.id">
                {{client.first_name}} {{client.last_name}}
              </mat-option>
            </mat-select>
          </mat-form-field>
        </div>
        
        <div class="form-group checkbox">
          <mat-checkbox formControlName="is_scan">Is this a scan appointment?</mat-checkbox>
        </div>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="onCancel()">Cancel</button>
      <button mat-raised-button color="primary" (click)="onSubmit()" [disabled]="eventForm.invalid">Save</button>
    </mat-dialog-actions>
  `,
  styles: [`
    .form-group {
      margin-bottom: 15px;
    }
  `]
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
