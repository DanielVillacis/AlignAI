import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private darkMode = new BehaviorSubject<boolean>(false);
  isDarkMode$ = this.darkMode.asObservable();

  constructor() {
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme) {
      this.darkMode.next(JSON.parse(savedTheme));
      this.updateTheme(JSON.parse(savedTheme));
    }
  }

  toggleDarkMode(): void {
    const newValue = !this.darkMode.value;
    this.darkMode.next(newValue);
    localStorage.setItem('darkMode', JSON.stringify(newValue));
    this.updateTheme(newValue);
  }

  private updateTheme(isDark: boolean): void {
    document.body.classList.toggle('dark-theme', isDark);
  }
}