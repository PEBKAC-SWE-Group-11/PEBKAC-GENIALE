import { Component } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './Core/Sidebar/Sidebar.component';
import { ChatboxComponent } from './Core/Chatbox/Chatbox.component';

@Component({
  selector: 'app-root',
  templateUrl: './App.component.html',
  styleUrls: ['./App.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    SidebarComponent,
    ChatboxComponent
  ]
})
export class AppComponent {
  title = 'GENIALE';
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
