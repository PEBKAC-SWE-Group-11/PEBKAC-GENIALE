export interface Conversation {
  // da aggiornare con i campi del backend
  conversationId: string;
  sessionId: string;
  createdAt: string;
  updatedAt: string;
  toDelete: boolean;
  title?: string;
  isWaiting?: boolean; // Indica se la conversazione è in attesa di una risposta
}