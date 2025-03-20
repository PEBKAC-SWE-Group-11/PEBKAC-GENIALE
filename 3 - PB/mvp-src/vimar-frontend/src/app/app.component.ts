import { Component } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './core/sidebar/sidebar.component';
import { ChatboxComponent } from './core/chatbox/chatbox.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    SidebarComponent,
    ChatboxComponent
  ]
})
export class AppComponent {
  title = 'Vimar GENIALE';
  sidebarVisible = false;
  
  constructor(private router: Router) {}
  
  isAdminRoute(): boolean {
    return this.router.url.startsWith('/admin');
  }
  
  toggleSidebar(): void {
    this.sidebarVisible = !this.sidebarVisible;
  }
  
  closeSidebarOnMobile(): void {
    if (window.innerWidth <= 768) {
      this.sidebarVisible = false;
    }
  }
}
