import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ClientService } from '../../services/client.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-client-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './client-profile.component.html',
  styleUrls: ['./client-profile.component.scss']
})
export class ClientProfileComponent implements OnInit {
  clientId!: number;
  client: any;
  isEditing: boolean = false;
  editedClient: any;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private clientService: ClientService
  ) { }

  ngOnInit(): void {
    this.clientId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadClient();
  }

  loadClient(): void {
    this.clientService.getClientById(this.clientId).subscribe({
      next: (data) => {
        this.client = data;
        this.editedClient = { ...data };
      },
      error: (error) => console.error('Error loading client:', error)
    });
  }

  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    if (!this.isEditing) {
      this.editedClient = { ...this.client };
    }
  }

  saveChanges(): void {
    this.clientService.updateClient(this.clientId, this.editedClient).subscribe({
      next: () => {
        this.client = { ...this.editedClient };
        this.isEditing = false;
      },
      error: (error) => console.error('Error updating client:', error)
    });
  }

  deleteClient(): void {
    if (confirm('Are you sure you want to delete this client?')) {
      this.clientService.deleteClient(this.clientId).subscribe({
        next: () => {
          this.router.navigate(['/clients']);
        },
        error: (error) => console.error('Error deleting client:', error)
      });
    }
  }

  goBack(): void {
    this.router.navigate(['/clients']);
  }
}