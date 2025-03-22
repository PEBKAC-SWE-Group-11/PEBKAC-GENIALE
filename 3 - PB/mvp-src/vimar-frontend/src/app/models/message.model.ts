import { Feedback } from './feedback.model';

export interface Message {
  message_id: string;
  conversation_id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  feedback?: Feedback;
}