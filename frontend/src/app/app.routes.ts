import { Routes } from '@angular/router';
import { HomePageComponent } from './home-page/home-page.component';
import { ScanPageComponent } from './scan-page/scan-page.component';
import { ClientPageComponent } from './client-page/client-page.component';
import { CreateClientPageComponent } from './create-client-page/create-client-page.component';

export const routes: Routes = [
    { path: '', component: HomePageComponent },
    { path: 'scan', component: ScanPageComponent },
    { path: 'clients', component: ClientPageComponent },
    // { path: 'clients/:id', component: ClientDetailComponent },
    { path: 'clients/new', component: CreateClientPageComponent }
];
