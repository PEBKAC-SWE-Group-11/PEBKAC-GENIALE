import { Component, OnInit, OnDestroy, Input } from '@angular/core';
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
  
  @Input() toggleSidebar: () => void = () => {};

  feedbackMessageId: string | null = null;
  feedbackIsPositive: boolean = false;
  feedbackContent: string = '';
  showFeedbackPopup: boolean = false;
  readonly MAX_FEEDBACK_LENGTH: number = 300;

  constructor(private chatService: ChatService) {
    this.messages$ = this.chatService.messages$;
  }

  ngOnInit(): void {
    this.subscriptions.add(
      this.chatService.activeConversation$.subscribe(conversation => {
        this.activeConversation = conversation;
      })
    );
    
    // Aggiungiamo log per debug
    this.subscriptions.add(
      this.messages$.subscribe(messages => {
        console.log('Messaggi ricevuti:', messages);
        if (messages.length === 0) {
          console.log('Nessun messaggio ricevuto per la conversazione attuale');
        }
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
    this.feedbackMessageId = messageId;
    this.feedbackIsPositive = true;
    this.feedbackContent = '';
    this.showFeedbackPopup = true;
  }

  sendNegativeFeedback(messageId: string): void {
    this.feedbackMessageId = messageId;
    this.feedbackIsPositive = false;
    this.feedbackContent = '';
    this.showFeedbackPopup = true;
  }

  submitFeedback(): void {
    if (!this.feedbackMessageId) return;
    
    const content = this.feedbackContent.trim() || undefined;
    
    this.chatService.sendFeedback(
      this.feedbackMessageId, 
      this.feedbackIsPositive, 
      content
    );
    this.closeFeedbackPopup();
  }

  closeFeedbackPopup(): void {
    this.showFeedbackPopup = false;
    this.feedbackMessageId = null;
  }

  get remainingFeedbackChars(): number {
    return this.MAX_FEEDBACK_LENGTH - this.feedbackContent.length;
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

  onToggleSidebar(): void {
    this.toggleSidebar();
  }
}
