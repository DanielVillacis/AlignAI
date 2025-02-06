import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { SideBarComponent } from '../side-bar/side-bar.component'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule, SideBarComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent { }
