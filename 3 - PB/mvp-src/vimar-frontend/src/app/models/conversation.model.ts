export interface Conversation {
  // da aggiornare con i campi del backend
  conversation_id: string;
  session_id: string;
  created_at: string;
  updated_at: string;
  to_delete: boolean;
  title?: string;
}