import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, forkJoin, of } from 'rxjs';
import { map, delay } from 'rxjs/operators';
import { Message } from '../Models/Message.model';
import { Conversation } from '../Models/Conversation.model';
import { environment } from '../../../Environment/Environment';

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

  createSession(): Observable<{sessionId: string}> {
    return this.http.post<{sessionId: string}>(`${this.apiUrl}/api/session`, {}, 
      { headers: this.getHeaders() });
  }

  readSession(sessionId: string): Observable<{sessionId: string, isActive: boolean}> {
    return this.http.get<{sessionId: string, isActive: boolean}>(`${this.apiUrl}/api/session/${sessionId}`, {
      headers: this.getHeaders()
    });
  }

  updateSession(sessionId: string): Observable<{success: boolean}> {
    return this.http.put<{success: boolean}>(`${this.apiUrl}/api/session/${sessionId}`, {}, 
      { headers: this.getHeaders() });
  }

  getConversations(sessionId: string): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(`${this.apiUrl}/api/conversation`, {
      headers: this.getHeaders(),
      params: { sessionId: sessionId }
    });
  }

  createConversation(sessionId: string): Observable<{conversationId: string}> {
    return this.http.post<{conversationId: string}>(`${this.apiUrl}/api/conversation`, 
      { sessionId: sessionId },
      { headers: this.getHeaders() });
  }

  deleteConversation(conversationId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/api/conversation/${conversationId}`, 
      { headers: this.getHeaders() });
  }

  getMessages(conversationId: string): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.apiUrl}/api/message`, {
      headers: this.getHeaders(),
      params: { conversationId: conversationId }
    });
  }

  sendMessage(conversationId: string, content: string): Observable<{messageId: string}> {
    return this.http.post<{messageId: string}>(`${this.apiUrl}/api/message`, 
      { 
        conversationId: conversationId,
        sender: 'user',
        content 
      },
      { headers: this.getHeaders() });
  }

  askQuestion(conversationId: string, question: string): Observable<{messageId: string}> {
    return this.http.post<{messageId: string}>(
      `${this.apiUrl}/api/question/${conversationId}`,
      { question: question },
      { headers: this.getHeaders() }
    );
  }

  sendFeedback(messageId: string, isPositive: boolean, content?: string): Observable<{messageId: string}> {
    return this.http.post<{messageId: string}>(`${this.apiUrl}/api/feedback`, 
      { 
        messageId: messageId,
        feedbackValue: isPositive ? 1 : 0,
        content: content || null
      },
      { headers: this.getHeaders() });
  }

  getAdminStats(): Observable<{
    totalConversations: number,
    positiveFeedback: number,
    negativeFeedback: number
  }> {
    const headers = this.getHeaders();
    
    return forkJoin({
      numConversations: this.http.get<{numConversations: number}>(`${this.apiUrl}/api/dashboard/numConversations`, { headers })
        .pipe(map(res => res.numConversations)),
      numPositiveFeedback: this.http.get<{numPositiveFeedback: number}>(`${this.apiUrl}/api/dashboard/numPositive`, { headers })
        .pipe(map(res => res.numPositiveFeedback)),
      numNegativeFeedback: this.http.get<{numNegativeFeedback: number}>(`${this.apiUrl}/api/dashboard/numNegative`, { headers })
        .pipe(map(res => res.numNegativeFeedback))
    }).pipe(
      map(result => ({
        totalConversations: result.numConversations,
        positiveFeedback: result.numPositiveFeedback,
        negativeFeedback: result.numNegativeFeedback,
        totalMessages: 0,
        uniqueUsers: 0
      }))
    );
  }

  getFeedbackWithComments(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/api/dashboard/feedbackComments`, {
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
