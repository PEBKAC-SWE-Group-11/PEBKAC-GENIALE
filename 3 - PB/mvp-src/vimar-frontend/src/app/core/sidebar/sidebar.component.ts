import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService } from '../../services/chat.service';
import { Conversation } from '../../models/conversation.model';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css'],
  standalone: true,
  imports: [CommonModule]
})
export class SidebarComponent implements OnInit, OnDestroy {
  conversations: Conversation[] = [];
  activeConversation: Conversation | null = null;
  
  private subscriptions: Subscription = new Subscription();

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.subscriptions.add(
      this.chatService.conversations$.subscribe(conversations => {
        this.conversations = conversations;
      })
    );

    this.subscriptions.add(
      this.chatService.activeConversation$.subscribe(conversation => {
        this.activeConversation = conversation;
      })
    );
  }
  
  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  createNewConversation(): void {
    this.chatService.createConversation().catch(error => {
      console.error('Errore durante la creazione della conversazione:', error);
      alert('Impossibile creare una nuova conversazione: ' + error.message);
    });
  }

  selectConversation(conversation: Conversation): void {
    this.chatService.setActiveConversation(conversation);
  }

  deleteConversation(event: Event, conversationId: string): void {
    event.stopPropagation();
    if (confirm('Sei sicuro di voler eliminare questa conversazione?')) {
      this.chatService.deleteConversation(conversationId).catch(error => {
        console.error('Errore durante l\'eliminazione della conversazione:', error);
        alert('Impossibile eliminare la conversazione: ' + error.message);
      });
    }
  }

  isActive(conversation: Conversation): boolean {
    return this.activeConversation?.conversation_id === conversation.conversation_id;
  }
}
