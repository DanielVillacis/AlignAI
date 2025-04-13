import { Routes } from '@angular/router';
import { HomePageComponent } from './components/Home/home-page/home-page.component';
import { ScanPageComponent } from './components/Scan/scan-page/scan-page.component';
import { ClientPageComponent } from './components/Clients/client-page/client-page.component';
import { CreateClientPageComponent } from './components/Clients/create-client-page/create-client-page.component';
import { ClientProfileComponent } from './components/Clients/client-profile/client-profile.component';
import { LoginComponent } from './components/Login/login/login.component';
import { RegisterComponent } from './components/Login/register/register.component';
import { OptionsPageComponent } from './components/Options/options-page/options-page.component';
import { AuthGuard } from './guards/auth.guard';


export const routes: Routes = [
    { path: 'login', component: LoginComponent },
    { path: 'register', component: RegisterComponent },
    { path: '', component: HomePageComponent, canActivate: [AuthGuard] },
    { path: 'scan', component: ScanPageComponent, canActivate: [AuthGuard] },
    { path: 'clients', component: ClientPageComponent, canActivate: [AuthGuard] },
    { path: 'clients/new', component: CreateClientPageComponent, canActivate: [AuthGuard] },
    { path: 'clients/:id', component: ClientProfileComponent, canActivate: [AuthGuard] },
    { path: 'options', component: OptionsPageComponent, canActivate: [AuthGuard] },
    { path: '**', redirectTo: '' }
];
