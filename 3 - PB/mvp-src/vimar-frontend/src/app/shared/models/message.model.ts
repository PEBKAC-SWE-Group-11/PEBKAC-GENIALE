import { Feedback } from './feedback.model';

export interface Message {
  messageId: string;
  conversationId: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: string;
  feedback?: Feedback;
}