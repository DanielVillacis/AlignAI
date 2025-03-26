import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ThemeService } from '../../services/theme.service';


@Component({
  selector: 'app-theme-toggle',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './theme-toggle.component.html',
  styleUrl: './theme-toggle.component.scss'
})

export class ThemeToggleComponent {
  constructor(private themeService: ThemeService) {}

  get isDarkMode$() {
    return this.themeService.isDarkMode$;
  }

  toggleTheme(): void {
    this.themeService.toggleDarkMode();
  }
}
