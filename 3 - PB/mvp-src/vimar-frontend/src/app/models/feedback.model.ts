export interface Feedback {
  feedback_id: string;
  message_id: string;
  type: 'positive' | 'negative';
  content?: string | null;
  created_at: string;
} 