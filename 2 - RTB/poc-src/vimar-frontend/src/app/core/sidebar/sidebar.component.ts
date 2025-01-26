import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { firstValueFrom, BehaviorSubject } from 'rxjs';
import { Conversation } from '../../models/conversation.model';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css'
})
export class SidebarComponent {
  private conversationsSubject = new BehaviorSubject<Conversation[]>([]);
  conversations$ = this.conversationsSubject.asObservable();

  @Output() addConversationClick = new EventEmitter<void>();
  @Output() conversationSelected = new EventEmitter<number>();
  @Output() conversationDeleted = new EventEmitter<number>();
  activeConversationId: number = 0;

  constructor(
    private apiService: ApiService
  ) {}

  async ngOnInit() {
    await this.loadConversations();
  }  
  
  async loadConversations() {
    try {
      const conversations = await firstValueFrom(
        this.apiService.getConversations()
      );
      
      const sortedConversations = conversations.sort((a, b) => b.conversation_id - a.conversation_id);
      this.conversationsSubject.next(sortedConversations);

    } catch (error) {
      console.error('Errore nel recupero delle conversazioni:', error);
      this.conversationsSubject.next([]);
    }
  }

  async selectConversation(conversationId: number) {
    try {
      
      this.conversationSelected.emit(conversationId);
      this.activeConversationId = conversationId;
      await this.loadConversations();

    } catch (error) {
      console.error('Errore nella selezione della conversazione:', error);
    }
  }

  async onAddClick() {
    try {
      this.addConversationClick.emit();
    } catch (error) {
      console.error('Errore nella preparazione per nuova conversazione:', error);
    }
  }

  setActiveConversation(conversationId: number) {
    this.activeConversationId = conversationId;
  }

  async deleteConversation(conversationId: number, event: Event) {
    try {
      event.stopPropagation();
      
      if (confirm('Sei sicuro di voler eliminare questa conversazione?')) {
        await firstValueFrom(this.apiService.deleteConversation(conversationId));
        
        if (conversationId === this.activeConversationId) {
          this.activeConversationId = 0;
          this.conversationDeleted.emit(conversationId);
        }
        
        await this.loadConversations();
      }

    } catch (error) {
      console.error('Errore nell\'eliminazione della conversazione:', error);
    }
  }
}
