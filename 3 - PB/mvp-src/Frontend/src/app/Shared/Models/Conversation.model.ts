export interface Conversation {
  conversationId: string;
  sessionId: string;
  createdAt: string;
  updatedAt: string;
  toDelete: boolean;
  title?: string;
  isWaiting?: boolean;
}