import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { Message } from '../../models/message.model';
import { Conversation } from '../../models/conversation.model';

@Component({
  selector: 'app-chatbox',
  templateUrl: './chatbox.component.html',
  styleUrls: ['./chatbox.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule]
})
export class ChatboxComponent implements OnInit {
  messages: Message[] = [];
  activeConversation: Conversation | null = null;
  newMessage: string = '';
  readonly MAX_MESSAGE_LENGTH = 500;
  isLoading: boolean = false;

  constructor(private chatService: ChatService) {}

  ngOnInit(): void {
    this.chatService.messages$.subscribe(messages => {
      this.messages = messages;
    });

    this.chatService.activeConversation$.subscribe(conversation => {
      this.activeConversation = conversation;
    });
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
}
