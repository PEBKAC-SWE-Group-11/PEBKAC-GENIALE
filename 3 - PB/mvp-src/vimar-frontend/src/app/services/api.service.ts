import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Message } from '../models/message.model';
import { Conversation } from '../models/conversation.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  createSession(): Observable<{sessionId: string}> {
    return this.http.post<{sessionId: string}>(`${this.apiUrl}/sessions`, {});
  }

  getConversations(sessionId: string): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(`${this.apiUrl}/sessions/${sessionId}/conversations`);
  }

  createConversation(sessionId: string): Observable<Conversation> {
    return this.http.post<Conversation>(`${this.apiUrl}/sessions/${sessionId}/conversations`, {});
  }

  deleteConversation(sessionId: string, conversationId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/sessions/${sessionId}/conversations/${conversationId}`);
  }

  getMessages(sessionId: string, conversationId: string): Observable<Message[]> {
    return this.http.get<Message[]>(
      `${this.apiUrl}/sessions/${sessionId}/conversations/${conversationId}/messages`
    );
  }

  sendMessage(sessionId: string, conversationId: string, content: string): Observable<Message> {
    return this.http.post<Message>(
      `${this.apiUrl}/sessions/${sessionId}/conversations/${conversationId}/messages`,
      { content }
    );
  }

  sendFeedback(sessionId: string, messageId: string, isPositive: boolean): Observable<void> {
    return this.http.post<void>(
      `${this.apiUrl}/sessions/${sessionId}/messages/${messageId}/feedback`,
      { isPositive }
    );
  }

  adminLogin(passwordHash: string): Observable<{success: boolean, token?: string}> {
    return this.http.post<{success: boolean, token?: string}>(
      `${this.apiUrl}/admin/login`, 
      { passwordHash }
    );
  }

  getAdminStats(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/admin/stats`);
  }
}
