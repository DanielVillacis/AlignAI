import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { environment } from '../../environments/environment.local';


@Injectable({
    providedIn: 'root'
  })

export class AuthService {
    private apiUrl = `${environment.apiUrl}/auth`;
    private userSubject = new BehaviorSubject<any>(null);
    public user$ = this.userSubject.asObservable();
    private tokenExpiryTimer: any;

    constructor(
        private http: HttpClient,
        private router: Router
    ) {
        this.loadUserFromStorage();
    }

    private loadUserFromStorage() {
        const userData = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        const refreshToken = localStorage.getItem('refreshToken');
        const tokenExpiry = localStorage.getItem('tokenExpiry');

        if (userData && token && refreshToken) {
            const user = JSON.parse(userData); // parse the user data
            this.userSubject.next(user); // emit the user data

            // set token expiry timer
            if (tokenExpiry) {
                const expiresIn = new Date(tokenExpiry).getTime() - Date.now();
                if (expiresIn > 0) {
                    this.setTokenExpiry(expiresIn);
                } else {
                    this.refreshToken();
                }
            }
        }
    }

    register(userData: any) : Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/register`, userData).pipe(
            tap(response => this.handleAuthResponse(response)),
            catchError(this.handleError)
        );
    }

    login(email: string, password: string): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/login`, { email, password }).pipe(
            tap(response => this.handleAuthResponse(response)),
            catchError(this.handleError)
        );
    }
    
    googleLogin(idToken: string): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/google`, { id_token: idToken }).pipe(
            tap(response => this.handleAuthResponse(response)),
            catchError(this.handleError)
        );
    }
    
    appleLogin(identityToken: string): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/apple`, { identity_token: identityToken }).pipe(
            tap(response => this.handleAuthResponse(response)),
            catchError(this.handleError)
        );
    }

    refreshToken(): Observable<any> {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          this.logout();
          return of(null);
        }
    
        return this.http.post<any>(`${this.apiUrl}/refresh-token`, { refresh_token: refreshToken }).pipe(
          tap(response => {
            if (response && response.access_token) {
              localStorage.setItem('token', response.access_token);
              
              // set token expiry time (1 hour from now)
              const expiryDate = new Date(Date.now() + 3600 * 1000).toISOString();
              localStorage.setItem('tokenExpiry', expiryDate);
              
              // set new timer
              this.setTokenExpiry(3600 * 1000);
            }
          }),
          catchError(() => {
            this.logout();
            return of(null);
          })
        );
    }

    logout(): void {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('tokenExpiry');
        this.userSubject.next(null);
        if (this.tokenExpiryTimer) {
          clearTimeout(this.tokenExpiryTimer);
        }
        this.router.navigate(['/login']);
    }

    getToken(): string | null {
        return localStorage.getItem('token');
    }
    
    isAuthenticated(): boolean {
        return !!this.userSubject.value;
    }


    private handleAuthResponse(response: any): void {
        if (response && response.user && response.access_token && response.refresh_token) {
          // store user details and tokens
          localStorage.setItem('user', JSON.stringify(response.user));
          localStorage.setItem('token', response.access_token);
          localStorage.setItem('refreshToken', response.refresh_token);
          
          // set token expiry time (1 hour from now)
          const expiryDate = new Date(Date.now() + 3600 * 1000).toISOString();
          localStorage.setItem('tokenExpiry', expiryDate);
          
          // update user subject
          this.userSubject.next(response.user);
          
          // set token expiry timer
          this.setTokenExpiry(3600 * 1000);
        }
    }

    private setTokenExpiry(expiresIn: number): void {
        // clear any existing timer
        if (this.tokenExpiryTimer) {
            clearTimeout(this.tokenExpiryTimer);
        }
        
        // set new timer to refresh token 5 minutes before expiry
        const refreshTime = expiresIn - (5 * 60 * 1000);
        if (refreshTime > 0) {
            this.tokenExpiryTimer = setTimeout(() => {
                this.refreshToken().subscribe();
            }, refreshTime);
        }
    }
    
    private handleError(error: any): Observable<never> {
        console.error('Authentication error:', error);
        throw error;
    }

}
