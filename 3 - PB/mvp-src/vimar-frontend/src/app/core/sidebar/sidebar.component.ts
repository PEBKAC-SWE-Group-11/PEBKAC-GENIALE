import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService } from '../../services/chat.service';
import { Conversation } from '../../models/conversation.model';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
  standalone: true,
  imports: [CommonModule]
})
export class SidebarComponent implements OnInit {
  conversations: Conversation[] = [];
  activeConversation: Conversation | null = null;

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.chatService.conversations$.subscribe(conversations => {
      this.conversations = conversations;
    });

    this.chatService.activeConversation$.subscribe(conversation => {
      this.activeConversation = conversation;
    });
  }

  createNewConversation(): void {
    this.chatService.createConversation().catch(error => {
      alert(error.message);
    });
  }

  selectConversation(conversation: Conversation): void {
    this.chatService.setActiveConversation(conversation);
  }

  deleteConversation(event: Event, conversationId: string): void {
    event.stopPropagation();
    if (confirm('Sei sicuro di voler eliminare questa conversazione?')) {
      this.chatService.deleteConversation(conversationId);
    }
  }

  isActive(conversation: Conversation): boolean {
    return this.activeConversation?.id === conversation.id;
  }

  updateConversations(): void {
    this.chatService.conversations$.subscribe(conversations => {
      this.conversations = conversations;
    });
  }
}
