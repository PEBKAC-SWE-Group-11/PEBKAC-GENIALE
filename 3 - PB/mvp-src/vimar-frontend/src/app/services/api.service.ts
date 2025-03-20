import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, forkJoin, of } from 'rxjs';
import { map, delay } from 'rxjs/operators';
import { Message } from '../models/message.model';
import { Conversation } from '../models/conversation.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;
  private apiKey = environment.apiKey;

  constructor(private http: HttpClient) {}
  
  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'x-api-key': this.apiKey,
      'Content-Type': 'application/json'
    });
  }

  // Sessione
  createSession(): Observable<{session_id: string}> {
    return this.http.post<{session_id: string}>(`${this.apiUrl}/api/session`, {}, 
      { headers: this.getHeaders() });
  }

  updateSession(session_id: string): Observable<{success: boolean}> {
    return this.http.put<{success: boolean}>(`${this.apiUrl}/api/session/${session_id}`, {}, 
      { headers: this.getHeaders() });
  }

  // Conversazioni
  getConversations(session_id: string): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(`${this.apiUrl}/api/conversation`, {
      headers: this.getHeaders(),
      params: { session_id: session_id }
    });
  }

  getConversationById(conversation_id: string): Observable<Conversation> {
    return this.http.get<Conversation>(`${this.apiUrl}/api/conversation/${conversation_id}`, {
      headers: this.getHeaders()
    });
  }

  createConversation(session_id: string): Observable<{conversation_id: string}> {
    return this.http.post<{conversation_id: string}>(`${this.apiUrl}/api/conversation`, 
      { session_id: session_id },
      { headers: this.getHeaders() });
  }

  deleteConversation(conversation_id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/api/conversation/${conversation_id}`, 
      { headers: this.getHeaders() });
  }

  updateConversationTimestamp(conversation_id: string): Observable<{success: boolean}> {
    return this.http.put<{success: boolean}>(
      `${this.apiUrl}/api/conversation/${conversation_id}/update`, 
      {}, 
      { headers: this.getHeaders() }
    );
  }

  // Messaggi
  getMessages(conversation_id: string): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.apiUrl}/api/message`, {
      headers: this.getHeaders(),
      params: { conversation_id: conversation_id }
    });
  }

  sendMessage(conversationId: string, content: string): Observable<{message_id: string}> {
    return this.http.post<{message_id: string}>(`${this.apiUrl}/api/message`, 
      { 
        conversation_id: conversationId,
        sender: 'user',
        content 
      },
      { headers: this.getHeaders() });
  }

  // Feedback
  sendFeedback(message_id: string, is_positive: boolean, content?: string): Observable<{message_id: string}> {
    return this.http.post<{message_id: string}>(`${this.apiUrl}/api/feedback`, 
      { 
        message_id: message_id,
        feedback_value: is_positive ? 1 : 0,
        content: content || null
      },
      { headers: this.getHeaders() });
  }

  // Dashboard (Admin)
  getAdminStats(): Observable<{
    totalConversations: number,
    positiveFeedback: number,
    negativeFeedback: number
  }> {
    const headers = this.getHeaders();
    
    return forkJoin({
      num_conversations: this.http.get<{num_conversations: number}>(`${this.apiUrl}/api/dashboard/num_conversations`, { headers })
        .pipe(map(res => res.num_conversations)),
      num_positive_feedback: this.http.get<{num_positive_feedback: number}>(`${this.apiUrl}/api/dashboard/num_positive`, { headers })
        .pipe(map(res => res.num_positive_feedback)),
      num_negative_feedback: this.http.get<{num_negative_feedback: number}>(`${this.apiUrl}/api/dashboard/num_negative`, { headers })
        .pipe(map(res => res.num_negative_feedback))
    }).pipe(
      map(result => ({
        totalConversations: result.num_conversations,
        positiveFeedback: result.num_positive_feedback,
        negativeFeedback: result.num_negative_feedback,
        // Valori predefiniti per altri campi nel dashboard
        totalMessages: 0,
        uniqueUsers: 0
      }))
    );
  }

  getFeedbackWithComments(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/api/dashboard/feedback_comments`, {
      headers: this.getHeaders()
    });
  }

  adminLogin(passwordHash: string): Observable<{success: boolean, token?: string}> {
    // MOCK: 
    const mockAdminHash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"; // hash di "password"
    
    return of({
      success: passwordHash === mockAdminHash,
      token: passwordHash === mockAdminHash ? "mock-admin-token-123" : undefined
    }).pipe(
      delay(800)
    );
  }
}
