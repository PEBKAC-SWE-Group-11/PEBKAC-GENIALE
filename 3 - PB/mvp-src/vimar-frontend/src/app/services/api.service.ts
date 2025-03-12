import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Conversation } from '../models/conversation.model';
import { Message } from '../models/message.model';
import { Session } from '../models/session.model';



@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5001/api';
  private apiKey = 'our-secret-api-key';
  private readonly FIXED_SESSION_ID = 'session-1234567890';

  constructor(
    private http: HttpClient
  ) {}

  private getHeaders() {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'x-api-key': this.apiKey
    });
  }

  getCurrentSession(): Observable<Session> {
    console.log('Using fixed session:', this.FIXED_SESSION_ID);
    return this.http.get<Session>(
      `${this.apiUrl}/session/${this.FIXED_SESSION_ID}`, 
      { headers: this.getHeaders() }
    );
  }

  // Conversation APIs
  createConversation(): Observable<Conversation> {
    console.log('Creating conversation with fixed session:', this.FIXED_SESSION_ID);
    return this.http.post<Conversation>(
      `${this.apiUrl}/conversation`, 
      { session_id: this.FIXED_SESSION_ID }, 
      { headers: this.getHeaders() }
    );
  }

  getConversations(): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(
      `${this.apiUrl}/conversation`,
      { 
        params: { session_id: this.FIXED_SESSION_ID },
        headers: this.getHeaders() 
      }
    );
  }

  getConversationById(conversationId: number): Observable<Conversation> {
    return this.http.get<Conversation>(
      `${this.apiUrl}/conversation/${conversationId}`, 
      { headers: this.getHeaders() }
    );
  }

  deleteConversation(conversationId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/conversation/${conversationId}`, 
      { headers: this.getHeaders() });
  }

  // Message APIs
  addMessage(conversationId: number, content: string, sender: 'user'|'assistant'): Observable<Message> {
    return this.http.post<Message>(`${this.apiUrl}/message`, {
      conversation_id: conversationId,
      content,
      sender
    }, { headers: this.getHeaders() });
  }

  getMessages(conversationId: number): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.apiUrl}/message`, 
      { 
        params: { conversation_id: conversationId },
        headers: this.getHeaders() 
      });
  }

  // Question API
  askQuestion(conversationId: number, question: string): Observable<Message> {
    return this.http.post<Message>(
        `${this.apiUrl}/question/${conversationId}`, 
        { question: question },
        { headers: this.getHeaders() }
    );
  }
}
