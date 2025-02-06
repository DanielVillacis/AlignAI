import { Routes } from '@angular/router';
import { AppComponent } from './home-page/home-page.component';
import { ScanPageComponent } from './scan-page/scan-page.component';

export const routes: Routes = [
    { path: '', component: AppComponent },
    { path: 'scan', component: ScanPageComponent }
];
