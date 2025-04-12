import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ScanService } from '../../../services/scan.service';
import { ClientService } from '../../../services/client.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSnackBarModule } from '@angular/material/snack-bar'; 

@Component({
  selector: 'scan-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatSnackBarModule],
  templateUrl: './scan-page.component.html',
  styleUrls: ['./scan-page.component.scss'],
})
export class ScanPageComponent implements OnInit {
  scanForm: FormGroup;
  clients: any[] = [];
  selectedClient: any = null;
  isSubmitting = false;

  constructor(
    private fb: FormBuilder,
    private scanService: ScanService,
    private clientService: ClientService,
    private snackBar: MatSnackBar
  ) {
    this.scanForm = this.fb.group({
      clientId: ['', Validators.required],
      scanReason: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadClients();
    
    // Watch for changes in the client selection
    this.scanForm.get('clientId')?.valueChanges.subscribe(clientId => {
      if (clientId) {
        this.updateSelectedClient(clientId);
      } else {
        this.selectedClient = null;
      }
    });
  }

  loadClients(): void {
    this.clientService.getClients().subscribe({
      next: (data) => {
        this.clients = data;
      },
      error: (error) => {
        console.error('Error loading clients:', error);
        this.snackBar.open('Failed to load patients', 'Close', { duration: 5000 });
      }
    });
  }

  updateSelectedClient(clientId: number): void {
    this.selectedClient = this.clients.find(client => client.id == clientId);
  }

  launchScan(): void {
    if (this.scanForm.invalid) {
      this.scanForm.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;
    const { clientId, scanReason } = this.scanForm.value;

    this.scanService.launchScan(clientId, scanReason).subscribe({
      next: (data) => {
        this.isSubmitting = false;
        this.snackBar.open('Scan launched successfully', 'Close', { duration: 5000 });
        console.log('Scan launched successfully', data);
      },
      error: (error) => {
        this.isSubmitting = false;
        this.snackBar.open('Error launching scan', 'Close', { duration: 5000 });
        console.error('Error launching scan', error);
      }
    });
  }
}