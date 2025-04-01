import { Component, OnInit, OnDestroy, Input, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../Shared/Services/Chat.service';
import { Message } from '../../Shared/Models/Message.model';
import { Conversation } from '../../Shared/Models/Conversation.model';
import { Observable, Subscription } from 'rxjs';

@Component({
  selector: 'app-chatbox',
  templateUrl: './Chatbox.component.html',
  styleUrls: ['./Chatbox.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule]
})
export class ChatboxComponent implements OnInit, OnDestroy, AfterViewChecked {
  messages: Message[] = [];
  activeConversation: Conversation | null = null;
  readonly MAX_MESSAGE_LENGTH = 500;
  
  messages$: Observable<Message[]>;
  messageText: string = '';
  
  private subscriptions: Subscription = new Subscription();
  private shouldScrollToBottom: boolean = false;
  
  @Input() toggleSidebar: () => void = () => {};
  @Input() isSidebarOpen: boolean = false;
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;

  feedbackMessageId: string | null = null;
  feedbackIsPositive: boolean = false;
  feedbackContent: string = '';
  showFeedbackPopup: boolean = false;
  readonly MAX_FEEDBACK_LENGTH: number = 300;

  constructor(private chatService: ChatService) {
    this.messages$ = this.chatService.messages$;
  }

  get isWaitingResponse(): boolean {
    return this.chatService.isWaitingForResponse;
  }

  ngOnInit(): void {
    this.subscriptions.add(
      this.chatService.activeConversation$.subscribe(conversation => {
        this.activeConversation = conversation;
        this.shouldScrollToBottom = true;
      })
    );
    
    this.subscriptions.add(
      this.messages$.subscribe(messages => {
        console.log('Messaggi ricevuti:', messages);
        if (messages.length === 0) {
          console.log('Nessun messaggio ricevuto per la conversazione attuale');
        } else {
          this.shouldScrollToBottom = true;
        }
      })
    );
  }

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  private scrollToBottom(): void {
    try {
      if (this.messagesContainer && this.messagesContainer.nativeElement) {
        const element = this.messagesContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) {
      console.error('Errore durante lo scroll:', err);
    }
  }

  async sendMessage(): Promise<void> {
    if (!this.messageText.trim() || this.isWaitingResponse) return;
    
    if (this.messageText.length > this.MAX_MESSAGE_LENGTH) {
        alert(`Il messaggio non può superare i ${this.MAX_MESSAGE_LENGTH} caratteri.`);
        return;
    }
    
    const messageContent = this.messageText;
    this.messageText = '';
    
    this.shouldScrollToBottom = true;
    
    try {
        await this.chatService.sendMessage(messageContent);
    } catch (error) {
        console.error('Errore durante l\'invio del messaggio:', error);
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
    if (this.messageText.length > this.MAX_MESSAGE_LENGTH) {
      this.messageText = this.messageText.substring(0, this.MAX_MESSAGE_LENGTH);
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
