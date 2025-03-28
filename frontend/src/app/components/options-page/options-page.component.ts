import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ThemeToggleComponent } from '../theme-toggle/theme-toggle.component';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button'; // For buttons
import { MatDividerModule } from '@angular/material/divider';
import { FormsModule } from '@angular/forms'; 


@Component({
  selector: 'app-options-page',
  standalone: true,
  imports: [ThemeToggleComponent, 
    CommonModule,
    FormsModule,  // Add FormsModule for ngModel
    MatSlideToggleModule,
    MatSelectModule,
    MatButtonModule,
    MatDividerModule],
  templateUrl: './options-page.component.html',
  styleUrl: './options-page.component.scss'
})
export class OptionsPageComponent {
  emailNotifications = true;
  pushNotifications = false;

  languages = ['English', 'French'];
  selectedLanguage = 'English';

  updateProfile() {
    // Navigate to the profile update page or open a dialog
  }
  
  changePassword() {
    // Navigate to the change password page or open a dialog
  }

  exportData() {
    // Trigger data export logic
  }

  resetToDefaults() {
    // Reset all settings to their default values
    this.emailNotifications = true;
    this.pushNotifications = false;
    this.selectedLanguage = 'English';
  }
}
