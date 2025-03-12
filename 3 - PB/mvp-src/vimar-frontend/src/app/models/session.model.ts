export interface Session {
  session_id: string;
  created_at?: Date;
  expires_at?: Date;
  metadata?: any;
}