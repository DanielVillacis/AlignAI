import { Routes } from '@angular/router';
import { HomePageComponent } from './components/home-page/home-page.component';
import { ScanPageComponent } from './components/scan-page/scan-page.component';
import { ClientPageComponent } from './components/client-page/client-page.component';
import { CreateClientPageComponent } from './components/create-client-page/create-client-page.component';
import { ClientProfileComponent } from './components/client-profile/client-profile.component';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },
    { path: 'register', component: RegisterComponent },
    { path: '', component: HomePageComponent, canActivate: [AuthGuard] },
    { path: 'scan', component: ScanPageComponent, canActivate: [AuthGuard] },
    { path: 'clients', component: ClientPageComponent, canActivate: [AuthGuard] },
    { path: 'clients/:id', component: ClientProfileComponent, canActivate: [AuthGuard] },
    { path: 'clients/new', component: CreateClientPageComponent, canActivate: [AuthGuard] },
    { path: '**', redirectTo: '' }
];
