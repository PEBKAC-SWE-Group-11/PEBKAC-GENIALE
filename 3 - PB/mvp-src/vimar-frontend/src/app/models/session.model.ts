export interface Session {
  // da aggiornare con i campi del backend
  session_id: string;
  created_at?: Date;
  expires_at?: Date;
  metadata?: any;
}