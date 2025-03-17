export interface Message {
  // da aggiornare con i campi del backend
  message_id: number;
  conversation_id: string;
  sender: string;
  content: string;
  created_at: string;
}