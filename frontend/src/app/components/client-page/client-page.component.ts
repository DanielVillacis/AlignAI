import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ClientService } from '../../services/client.service';

@Component({
  selector: 'app-client-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './client-page.component.html',
  styleUrl: './client-page.component.scss'
})
export class ClientPageComponent implements OnInit {
  searchTerm: string = '';
  clients: any[] = [];
  filteredClients: any[] = [];

  constructor(
    private clientService: ClientService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.getClients();
  }

  getClients() {
    this.clientService.getClients()
      .subscribe({
        next: (data) => {
          this.clients = data;
          this.filteredClients = data;
        },
        error: (error) => {
          console.error('There was an error!', error);
        }
      });
  }

  searchClients() {
    if (!this.searchTerm) {
      this.filteredClients = this.clients;
      return;
    }

    const searchTermLower = this.searchTerm.toLowerCase();
    this.filteredClients = this.clients.filter(client => 
      client.first_name.toLowerCase().includes(searchTermLower) ||
      client.last_name.toLowerCase().includes(searchTermLower) ||
      client.email.toLowerCase().includes(searchTermLower) ||
      client.telephone.toLowerCase().includes(searchTermLower)
    );
  }

  navigateToClient(clientId: number) {
    this.router.navigate(['/clients', clientId]);
  }

  navigateToCreateNewClient() {
    this.router.navigate(['clients/new']);
  }
}
