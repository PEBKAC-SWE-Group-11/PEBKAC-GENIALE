import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css'],
  standalone: true,
  imports: [CommonModule, RouterModule]
})
export class AdminDashboardComponent implements OnInit {
  stats: any = null;
  isLoading: boolean = true;
  error: string = '';

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadStats();
  }

  async loadStats(): Promise<void> {
    this.isLoading = true;
    this.error = '';

    try {
      this.stats = await this.apiService.getAdminStats().toPromise();
    } catch (error) {
      this.error = 'Errore nel caricamento delle statistiche';
      console.error('Errore API:', error);
    } finally {
      this.isLoading = false;
    }
  }

  calcSatisfactionRate(): string {
    if (!this.stats) return '0%';
    
    const total = this.stats.positiveFeedback + this.stats.negativeFeedback;
    if (total === 0) return '0%';
    
    const rate = (this.stats.positiveFeedback / total) * 100;
    return `${Math.round(rate)}%`;
  }

  logout(): void {
    localStorage.removeItem('admin_token');
    this.router.navigate(['/admin/login']);
  }
} 