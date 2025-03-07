import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-client-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './client-page.component.html',
  styleUrl: './client-page.component.scss'
})
export class ClientPageComponent {
  searchTerm: string = '';
  clients: any[] = [];

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.getClients();
  }

  getClients() {
    this.http.get<any[]>('http://127.0.0.1:5000/api/clients')
    .subscribe({
      next: (data) => {
        this.clients = data;
      },
      error: (error) => {
        console.error('There was an error!', error);
      }});
  }

  searchClients() {
    // search client logic
  }

  navigateToClient(clientId: number) {
    this.router.navigate(['/client', clientId]);
  }

  navigateToCreateNewClient() {
    this.router.navigate(['clients/new']);
  }

}
