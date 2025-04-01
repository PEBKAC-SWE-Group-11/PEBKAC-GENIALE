import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ApiService } from '../../../shared/services/Api.service';
import { Feedback } from '../../../shared/models/Feedback.model';
import { firstValueFrom } from 'rxjs';

interface FeedbackWithMessage extends Feedback {
  messageContent: string;
}

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './Dashboard.component.html',
  styleUrls: ['./Dashboard.component.css'],
  standalone: true,
  imports: [CommonModule, RouterModule]
})
export class AdminDashboardComponent implements OnInit {
  stats: any = null;
  isLoading: boolean = true;
  error: string = '';
  feedbackComments: FeedbackWithMessage[] = [];
  isLoadingComments: boolean = false;
  commentsError: string = '';

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadStats();
    this.loadFeedbackComments();
  }

  async loadStats(): Promise<void> {
    this.isLoading = true;
    this.error = '';
    try {
      this.stats = await firstValueFrom(this.apiService.getAdminStats());
    } catch (error) {
      this.error = 'Errore nel caricamento delle statistiche';
      console.error('Errore API:', error);
    } finally {
      this.isLoading = false;
    }
  }

  async loadFeedbackComments(): Promise<void> {
    this.isLoadingComments = true;
    this.commentsError = '';
    try {
      const result = await firstValueFrom(this.apiService.getFeedbackWithComments());
      this.feedbackComments = result || [];
    } catch (error) {
      this.commentsError = 'Errore nel caricamento dei commenti di feedback';
      console.error('Errore API commenti:', error);
    } finally {
      this.isLoadingComments = false;
    }
  }

  calcSatisfactionRate(): string {
    if (!this.stats) return '0%';
    const total = (this.stats.positiveFeedback || 0) + (this.stats.negativeFeedback || 0);
    if (total === 0) return '0%';
    const rate = ((this.stats.positiveFeedback || 0) / total) * 100;
    return `${Math.round(rate)}%`;
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('it-IT');
  }

  logout(): void {
    localStorage.removeItem('adminToken');
    this.router.navigate(['/admin/login']);
  }
} 