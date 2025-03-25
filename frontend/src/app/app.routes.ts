import { Routes } from '@angular/router';
import { HomePageComponent } from './components/home-page/home-page.component';
import { ScanPageComponent } from './components/scan-page/scan-page.component';
import { ClientPageComponent } from './components/client-page/client-page.component';
import { CreateClientPageComponent } from './components/create-client-page/create-client-page.component';
import { ClientProfileComponent } from './components/client-profile/client-profile.component';

export const routes: Routes = [
    { path: '', component: HomePageComponent },
    { path: 'scan', component: ScanPageComponent },
    { path: 'clients', component: ClientPageComponent },
    { path: 'clients/:id', component: ClientProfileComponent },
    { path: 'clients/new', component: CreateClientPageComponent }
];
