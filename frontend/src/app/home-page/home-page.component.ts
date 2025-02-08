import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.scss'],
})

export class HomePageComponent implements OnInit {
  clients: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.getClients();
  }

  getClients() {
    this.http.get<any[]>('http://127.0.0.1:5000/api/clients')
      .subscribe(
        (data) => { this.clients = data; },
        (error) => { console.error("Error fetching clients", error); }
      );
  }
}
