import { Component, ViewChild } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from './core/sidebar/sidebar.component';
import { ChatboxComponent } from './core/chatbox/chatbox.component';
import { ApiService } from './services/api.service';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterModule, 
    CommonModule, 
    SidebarComponent, 
    ChatboxComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Vimar GENIALE';
  isAddingConversation: boolean = false;
  activeConversationId: number = 0;

  @ViewChild('sidebar') sidebarComponent!: SidebarComponent;

  constructor(
    private apiService: ApiService
  ) {}

  async ngOnInit() {
    try {
      const session = await firstValueFrom(this.apiService.getCurrentSession());
      console.log('Sessione inizializzata:', session);
  
      this.isAddingConversation = true;
  
    } catch (error) {
      console.error('Errore durante l\'inizializzazione:', error);
      this.isAddingConversation = false;
    }

  }

  onAddConversation() { 
    this.isAddingConversation = true;
  }

  async onConversationSelected(event: number) {
    try {
      this.isAddingConversation = false;
      this.activeConversationId = event;
    } catch (error) {
      console.error('Errore nella selezione della conversazione:', error);
    }
  }

  async onConversationCreated(event: number) {
    try {
      this.activeConversationId = event;
      this.isAddingConversation = false;
      if(this.sidebarComponent) {
        await this.sidebarComponent.loadConversations();
        this.sidebarComponent.setActiveConversation(event);
      }
    } catch (error) {
      console.error('Errore nella creazione della conversazione:', error);
    }
  }

  async onConversationDeleted(conversationId: number) {
    if (this.activeConversationId === conversationId) {
      this.isAddingConversation = true;
      this.activeConversationId = 0;
    }
  }

}
