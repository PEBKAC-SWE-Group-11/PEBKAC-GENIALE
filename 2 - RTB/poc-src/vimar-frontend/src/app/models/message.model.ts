export interface Message {
  message_id: number;
  conversation_id: number;
  content: string;
  sender: 'user' | 'assistant';
  created_at?: Date;
}