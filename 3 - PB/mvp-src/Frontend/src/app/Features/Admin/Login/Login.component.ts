import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../../../Shared/Services/Api.service';
import { RouterModule } from '@angular/router';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-admin-login',
  templateUrl: './Login.component.html',
  styleUrls: ['./Login.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule]
})
export class AdminLoginComponent {
  password: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  async hashPassword(password: string): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
  }

  async login(): Promise<void> {
    if (!this.password) {
      this.errorMessage = 'Inserisci la password';
      return;
    }
    this.isLoading = true;
    this.errorMessage = '';
    try {
      const passwordHash = await this.hashPassword(this.password);
      const response = await firstValueFrom(this.apiService.adminLogin(passwordHash));
      if (response && response.success) {
        if (response.token) {
          localStorage.setItem('adminToken', response.token);
        } else {
          localStorage.setItem('adminAuthenticated', 'true');
        }
        this.router.navigate(['/admin/dashboard']);
      } else {
        this.errorMessage = 'Password non valida';
      }
    } catch (error) {
      this.errorMessage = 'Errore durante l\'autenticazione';
      console.error('Errore di login:', error);
    } finally {
      this.isLoading = false;
    }
  }
} 