import { Component, OnInit, AfterViewInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../../services/auth.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { faGoogle, faApple, }  from '@fortawesome/free-brands-svg-icons';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { Meta } from '@angular/platform-browser';
import { environment } from '../../../../environments/environment.local';


declare global {
  interface Window {
    google?: any;
    AppleID?: any;
  }
}

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule, 
    ReactiveFormsModule, 
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatDividerModule,
    MatIconModule,
    MatProgressSpinnerModule,
    FontAwesomeModule
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})


export class LoginComponent implements OnInit, AfterViewInit {
  loginForm: FormGroup;
  isLoading = false;
  hidePassword = true;
  faGoogle = faGoogle;
  faApple = faApple;

  private googleClientId = environment.googleClientId; 
  private appleClientId = environment.appleClientId; 
  private appleRedirectUri = environment.appleRedirectUri;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private snackBar: MatSnackBar,
    private meta: Meta
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.meta.addTag({
      name: 'appleid-signin-client-id',
      content: this.appleClientId
    });
    this.meta.addTag({
      name: 'appleid-signin-scope',
      content: 'name email'
    });
    this.meta.addTag({
      name: 'appleid-signin-redirect-uri',
      content: this.appleRedirectUri
    });
    this.meta.addTag({
      name: 'appleid-signin-state',
      content: 'signin'
    });
  }

  ngOnInit(): void {
    // if user is already logged in, redirect to home page
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/']);
    }
  }

  ngAfterViewInit(): void {
    this.initGoogleSignIn();
    this.initAppleSignIn();
  }

  private initGoogleSignIn(): void {
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: this.googleClientId,
        callback: this.handleGoogleSignIn.bind(this),
        auto_select: false,
        cancel_on_tap_outside: true
      });
      
      window.google.accounts.id.renderButton(
        document.getElementById("google-signin-button"),
        { theme: "outline", size: "large", width: '100%' }
      );
    } else {
      setTimeout(() => this.initGoogleSignIn(), 100);
    }
  }

  private initAppleSignIn(): void {
    if (window.AppleID) {
      try {
        window.AppleID.auth.init({
          clientId: this.appleClientId,
          scope: 'name email',
          redirectURI: this.appleRedirectUri,
          state: 'signin'
        });
      } catch (error) {
        console.error('Error initializing Apple Sign-In:', error);
      }
    } else {
      setTimeout(() => this.initAppleSignIn(), 100);
    }
  }

  private handleGoogleSignIn(response: any): void {
    // extract the ID token
    const idToken = response.credential;
    
    this.isLoading = true;
    
    // call service method
    this.authService.googleLogin(idToken).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (error) => {
        this.isLoading = false;
        this.snackBar.open(error?.error?.error || 'Google login failed', 'Close', {
          duration: 5000
        });
      }
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid || this.isLoading) {
      return;
    }

    this.isLoading = true;
    const { email, password } = this.loginForm.value;

    this.authService.login(email, password).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (error) => {
        this.isLoading = false;
        this.snackBar.open(error?.error?.error || 'Login failed', 'Close', {
          duration: 5000
        });
      }
    });
  }




  googleLogin(): void {
    // Trigger Google Sign-In
    if (window.google) {
      window.google.accounts.id.prompt();
    } else {
      this.snackBar.open('Google Sign-In is not available', 'Close', {
        duration: 5000
      });
    }
  }

  appleLogin(): void {
    try {
      window.AppleID.auth.signIn().then((response: any) => {
        // Extract identity token and user info
        const { authorization } = response;
        const identityToken = authorization.id_token;
        
        this.isLoading = true;
        
        this.authService.appleLogin(identityToken).subscribe({
          next: () => {
            this.router.navigate(['/']);
          },
          error: (error) => {
            this.isLoading = false;
            this.snackBar.open(error?.error?.error || 'Apple login failed', 'Close', {
              duration: 5000
            });
          }
        });
      }).catch((error: any) => {
        console.error('Apple Sign-In error:', error);
        this.snackBar.open('Apple Sign-In failed', 'Close', {
          duration: 5000
        });
      });
    } catch (error) {
      console.error('Error with Apple Sign-In:', error);
      this.snackBar.open('Apple Sign-In is not available', 'Close', {
        duration: 5000
      });
    }
  }

  goToSignup(): void {
    this.router.navigate(['/register']);
  }

  forgotPassword(): void {
    // Implement forgot password functionality
    // Redirect to a forgot password page or open a dialog
    this.snackBar.open('Forgot password functionality coming soon!', 'Close', {
      duration: 5000
    });
  }


}
