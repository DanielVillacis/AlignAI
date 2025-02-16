import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, Routes } from '@angular/router';
import { AppComponent } from './app/app-component/app.component';
import { HomePageComponent } from './app/home-page/home-page.component';
import { ScanPageComponent } from './app/scan-page/scan-page.component';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

const routes: Routes = [
  { path: '', component: HomePageComponent },
  { path: 'scan', component: ScanPageComponent }
];

bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient(),
    provideRouter(routes), provideAnimationsAsync()
  ],
}).catch(err => console.error(err));