export interface Feedback {
  feedbackId: string;
  messageId: string;
  type: 'positive' | 'negative';
  content?: string | null;
  createdAt: string;
} 