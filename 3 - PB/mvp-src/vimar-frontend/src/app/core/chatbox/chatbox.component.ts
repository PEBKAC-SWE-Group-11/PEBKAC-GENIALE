import { Component, Input, Output, EventEmitter, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { firstValueFrom, BehaviorSubject } from 'rxjs';
import { Message } from '../../models/message.model';


@Component({
  selector: 'app-chatbox',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbox.component.html',
  styleUrl: './chatbox.component.css'
})
export class ChatboxComponent {
  private messagesSubject = new BehaviorSubject<Message[]>([]);
  messages$ = this.messagesSubject.asObservable();

  @Input() isAddingConversation: boolean = false;
  @Input() activeConversationId: number = 0;
  @Output() conversationCreated = new EventEmitter<number>();

  messageText: string = '';
  isWaitingResponse: boolean = false;

  constructor(
    private apiService: ApiService
  ) {}

  async ngOnInit() {
    try {
        if (this.activeConversationId > 0) {
          await this.loadMessages();
        }
        else if (this.isAddingConversation === true) {
          await this.createNewConversation();
        }
    } catch (error) {
      console.error('Errore nel recupero delle conversazioni:', error);
      this.isAddingConversation = true;
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['activeConversationId'] && 
        !changes['activeConversationId'].firstChange && 
        changes['activeConversationId'].currentValue !== changes['activeConversationId'].previousValue) {
      console.log('Conversation changed to:', this.activeConversationId);
      this.loadMessages();
    }
  }

  async createNewConversation() {
    try {

      const newConversation = await firstValueFrom(
        this.apiService.createConversation()
      );

      this.isAddingConversation = false;
      this.activeConversationId = newConversation.conversation_id;
      this.messagesSubject.next([]);
      this.conversationCreated.emit(newConversation.conversation_id);

    } catch (error) {
      console.error('Errore nella creazione della conversazione:', error);
    }
  }
  
  async sendMessage() {
    if (!this.messageText?.trim() || this.isWaitingResponse === true) return;

    const messageContent = this.messageText;
    this.messageText = '';
    this.isWaitingResponse = true;
    
    await firstValueFrom(
      this.apiService.addMessage(this.activeConversationId, messageContent, 'user')
    );
    await this.loadMessages();
    
    await firstValueFrom(
      this.apiService.askQuestion(this.activeConversationId, messageContent)
    );
    await this.loadMessages();

    this.isWaitingResponse = false;
  }

  async loadMessages() {
    try {
      const messages = await firstValueFrom(
        this.apiService.getMessages(this.activeConversationId)
      );
      this.messagesSubject.next(messages);
    } catch (error) {
      console.error('Errore nel caricamento dei messaggi:', error);
    }
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      this.sendMessage();
    }
  }
}
