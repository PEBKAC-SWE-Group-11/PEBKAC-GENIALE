import { Component, OnInit, OnDestroy, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService } from '../../shared/services/chat.service';
import { Conversation } from '../../shared/models/conversation.model';
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
  
  @Output() conversationSelected = new EventEmitter<void>();
  @Output() newConversationCreated = new EventEmitter<void>();

  readonly MAX_CONVERSATIONS = 10;

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.subscriptions.add(
      this.chatService.conversations$.subscribe(conversations => {
        this.conversations = conversations;
        
        // Log per verificare l'ordinamento
        console.log('Conversazioni ordinate:', this.conversations.map(c => ({
          id: c.conversationId,
          updated: new Date(c.updatedAt).toLocaleString()
        })));
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

  get hasReachedLimit(): boolean {
    return this.chatService.hasReachedConversationLimit();
  }
  
  // Getter per verificare se l'applicazione è in attesa di una risposta
  get isWaitingForResponse(): boolean {
    return this.chatService.isWaitingForResponse;
  }

  createNewConversation(): void {
    // Non creare nuove conversazioni se in attesa
    if (this.isWaitingForResponse) return;
    
    this.chatService.createConversation()
      .then(() => {
        this.newConversationCreated.emit();
      })
      .catch(error => {
        console.error('Errore durante la creazione della conversazione:', error);
      });
  }

  selectConversation(conversation: Conversation, event?: Event): void {
    // Non cambiare conversazione se in attesa
    if (this.isWaitingForResponse) {
      // Previeni l'azione predefinita se viene fornito un evento
      if (event) event.preventDefault();
      return;
    }
    
    this.chatService.setActiveConversation(conversation);
    
    // Emettere evento quando si seleziona una conversazione
    this.conversationSelected.emit();
  }

  deleteConversation(event: Event, conversationId: string): void {
    // Ferma la propagazione per evitare di selezionare la conversazione mentre viene eliminata
    event.stopPropagation();
    
    // Non eliminare conversazioni se in attesa
    if (this.isWaitingForResponse) return;
    
    this.chatService.deleteConversation(conversationId);
  }

  isActive(conversation: Conversation): boolean {
    return this.activeConversation?.conversationId === conversation.conversationId;
  }
}
