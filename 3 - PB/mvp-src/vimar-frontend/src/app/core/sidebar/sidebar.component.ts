import { Component, OnInit, OnDestroy, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChatService } from '../../shared/services/chat.service';
import { Conversation } from '../../shared/models/conversation.model';
import { Subscription, Observable } from 'rxjs';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css'],
  standalone: true,
  imports: [CommonModule]
})
export class SidebarComponent implements OnInit, OnDestroy {
  activeConversation: Conversation | null = null;
  conversations$: Observable<Conversation[]>;
  private subscriptions: Subscription = new Subscription();
  
  @Output() conversationSelected = new EventEmitter<void>();
  @Output() newConversationCreated = new EventEmitter<void>();

  readonly MAX_CONVERSATIONS = 10;

  constructor(private chatService: ChatService) {
    this.conversations$ = this.chatService.conversations$;
  }

  ngOnInit(): void {
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
  
  get isWaitingForResponse(): boolean {
    return this.chatService.isWaitingForResponse;
  }

  createNewConversation(): void {
    if (this.isWaitingForResponse) return;
    if (this.hasReachedLimit) {
      const confirmDelete = window.confirm(
        `Hai raggiunto il limite massimo di ${this.MAX_CONVERSATIONS} conversazioni. ` +
        `Premendo OK verrà eliminata la conversazione più vecchia per fare spazio a quella nuova.`
      );
      if (!confirmDelete) {
        return;
      }
    }    
    this.chatService.createConversation()
      .then(() => {
        this.newConversationCreated.emit();
      })
      .catch(error => {
        console.error('Errore durante la creazione della conversazione:', error);
      });
  }

  selectConversation(conversation: Conversation, event?: Event): void {
    if (this.isWaitingForResponse) {
      if (event) event.preventDefault();
      return;
    }
    this.chatService.setActiveConversation(conversation);
    this.conversationSelected.emit();
  }

  deleteConversation(event: Event, conversationId: string): void {
    event.stopPropagation();
    if (this.isWaitingForResponse) return;
    this.chatService.deleteConversation(conversationId);
  }

  isActive(conversation: Conversation): boolean {
    return this.activeConversation?.conversationId === conversation.conversationId;
  }
}
