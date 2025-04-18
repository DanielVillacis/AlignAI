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
    
    // watch for changes in the client selection
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

        this.pollScanStatus(clientId);
      },
      error: (error) => {
        this.isSubmitting = false;
        this.snackBar.open('Error launching scan', 'Close', { duration: 5000 });
        console.error('Error launching scan', error);
      }
    });
  }

  pollScanStatus(clientId: number): void {
    const pollingInterval = 5000; // we poll every 5 seconds (race condition from the whole system)
    const maxAttempts = 60; // try for 5 minutes max
    let attempts = 0;
    
    const pollTimer = setInterval(() => {
      attempts++;
      this.scanService.checkLatestScanStatus(clientId).subscribe({
        next: (response) => {
          if (response.status === 'complete') {
            // scan is complete, stop polling and download report
            clearInterval(pollTimer);

            setTimeout(() => {
              this.downloadReport(response.scan_id);
            }, 1500); // 1.5 second delay

          } else if (attempts >= maxAttempts) {
            // stop polling after max attempts
            clearInterval(pollTimer);
            this.snackBar.open('Scan is taking longer than expected. Check results later.', 'Close', 
              { duration: 8000 });
          }
        },
        error: () => {
          if (attempts >= maxAttempts) {
            clearInterval(pollTimer);
          }
        }
      });
    }, pollingInterval);
  }

  downloadReport(scanId: number): void {
    this.scanService.downloadScanReport(scanId).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        
        // create a link element and trigger download
        const a = document.createElement('a');
        a.href = url;

        a.download = `client_${this.selectedClient?.id}_scan_report.pdf`;

        document.body.appendChild(a);
        a.click();
        
        // clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        this.snackBar.open('Scan report downloaded successfully', 'Close', { duration: 5000 });
      },
      error: (error) => {
        console.error('Error downloading scan report', error);
        this.snackBar.open('Error downloading scan report', 'Close', { duration: 5000 });
      }
    });
  }
}