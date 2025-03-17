import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { Message } from '../../models/message.model';
import { Conversation } from '../../models/conversation.model';
import { Observable, Subscription } from 'rxjs';

@Component({
  selector: 'app-chatbox',
  templateUrl: './chatbox.component.html',
  styleUrls: ['./chatbox.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule]
})
export class ChatboxComponent implements OnInit, OnDestroy {
  messages: Message[] = [];
  activeConversation: Conversation | null = null;
  newMessage: string = '';
  readonly MAX_MESSAGE_LENGTH = 500;
  isLoading: boolean = false;
  
  messages$: Observable<Message[]>;
  messageText: string = '';
  isWaitingResponse: boolean = false;
  
  private subscriptions: Subscription = new Subscription();

  constructor(private chatService: ChatService) {
    this.messages$ = this.chatService.messages$;
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

  async sendMessage(): Promise<void> {
    if (!this.newMessage.trim() || !this.activeConversation) return;
    
    if (this.newMessage.length > this.MAX_MESSAGE_LENGTH) {
      alert(`Il messaggio non può superare i ${this.MAX_MESSAGE_LENGTH} caratteri.`);
      return;
    }
    
    this.isLoading = true;
    
    try {
      await this.chatService.sendMessage(this.newMessage);
      this.newMessage = '';
    } catch (error) {
      console.error('Errore durante l\'invio del messaggio:', error);
    } finally {
      this.isLoading = false;
    }
  }

  sendPositiveFeedback(messageId: string): void {
    this.chatService.sendFeedback(messageId, true);
  }

  sendNegativeFeedback(messageId: string): void {
    this.chatService.sendFeedback(messageId, false);
  }

  checkMessageLength(): void {
    if (this.newMessage.length > this.MAX_MESSAGE_LENGTH) {
      this.newMessage = this.newMessage.substring(0, this.MAX_MESSAGE_LENGTH);
    }
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !this.isWaitingResponse) {
      this.sendMessage();
    }
  }
}
