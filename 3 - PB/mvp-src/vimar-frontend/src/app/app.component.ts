import { Component, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './core/sidebar/sidebar.component';
import { ChatboxComponent } from './core/chatbox/chatbox.component';
import { Conversation } from './models/conversation.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [RouterOutlet, SidebarComponent, ChatboxComponent]
})
export class AppComponent {
  title = 'Vimar Chat';
  isAddingConversation = false;
  activeConversationId: string | null = null;
  
  @ViewChild('sidebar') sidebarComponent!: SidebarComponent;
  
  onAddConversation(): void {
    this.isAddingConversation = true;
    this.activeConversationId = null;
  }
  
  onConversationSelected(conversation: Conversation): void {
    this.isAddingConversation = false;
    this.activeConversationId = conversation.id;
  }
  
  onConversationDeleted(conversationId: string): void {
    if (this.activeConversationId === conversationId) {
      this.activeConversationId = null;
    }
  }
  
  onConversationCreated(conversation: Conversation): void {
    this.isAddingConversation = false;
    this.activeConversationId = conversation.id;
    this.sidebarComponent.updateConversations();
  }
}
