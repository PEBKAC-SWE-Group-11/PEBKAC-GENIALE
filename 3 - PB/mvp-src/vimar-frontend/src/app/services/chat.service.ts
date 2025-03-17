import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, firstValueFrom } from 'rxjs';
import { Message } from '../models/message.model';
import { Conversation } from '../models/conversation.model';
import { ApiService } from './api.service';
import { Session } from '../models/session.model';

@Injectable({
    providedIn: 'root'
})

export class ChatService {
    private conversationsSubject = new BehaviorSubject<Conversation[]>([]);
    private activeConversationSubject = new BehaviorSubject<Conversation | null>(null);
    private messagesSubject = new BehaviorSubject<Message[]>([]);
    private currentSessionId: string = '';
    
    private readonly MAX_CONVERSATIONS = 10;
    private readonly MAX_MESSAGE_LENGTH = 500;
    
    private isWaitingResponse: boolean = false;

    private apiService = inject(ApiService);

    constructor() {
        this.initializeFromStorage();
    }

    get conversations$(): Observable<Conversation[]> {
        return this.conversationsSubject.asObservable();
    }

    get activeConversation$(): Observable<Conversation | null> {
        return this.activeConversationSubject.asObservable();
    }

    get messages$(): Observable<Message[]> {
        return this.messagesSubject.asObservable();
    }

    private async initializeFromStorage(): Promise<void> {
        this.currentSessionId = localStorage.getItem('session_id') || '';
        
        if (this.currentSessionId != '' && this.currentSessionId != null) {
            await this.loadConversations(this.currentSessionId);
        } else {
            await this.createNewSession();
        }
    }

    private async createNewSession(): Promise<void> {
        try {
            const response = await firstValueFrom(this.apiService.createSession());
            this.currentSessionId = response.session_id;
            localStorage.setItem('session_id', this.currentSessionId);
            
            await this.createConversation();
        } catch (error) {
            console.error('Errore durante la creazione della sessione:', error);
        }
    }

    private async loadConversations(sessionId: string): Promise<void> {
        try {
            const conversations = await firstValueFrom(this.apiService.getConversations(sessionId));
            this.conversationsSubject.next(conversations);
            
            if (conversations.length > 0) {
                this.setActiveConversation(conversations[0]);
            } else {
                await this.createConversation();
            }
        } catch (error) {
            console.error('Errore durante il caricamento delle conversazioni:', error);
            await this.createNewSession();
        }
    }

    async createConversation(): Promise<Conversation | null> {
        if (!this.currentSessionId) return null;
        
        try {
            const response = await firstValueFrom(
                this.apiService.createConversation(this.currentSessionId)
            );
            
            if (response && response.conversation_id) {
                const newConversation = {
                    conversation_id: response.conversation_id,
                    session_id: this.currentSessionId,
                    created_at: new Date().toISOString(),
                    title: `Conversazione ${response.conversation_id}`,
                    updated_at: new Date().toISOString()
                } as Conversation;
                
                const currentConversations = this.conversationsSubject.getValue();
                const updatedConversations = [newConversation, ...currentConversations];
                this.conversationsSubject.next(updatedConversations);
                this.setActiveConversation(newConversation);
                return newConversation;
            }
            return null;
        } catch (error) {
            console.error('Errore durante la creazione della conversazione:', error);
            throw error;
        }
    }

    setActiveConversation(conversation: Conversation): void {
        this.activeConversationSubject.next(conversation);
        this.loadMessages(conversation.conversation_id);
    }

    private async loadMessages(conversationId: string): Promise<void> {
        if (!this.currentSessionId || !conversationId) return;
        
        try {
            const messages = await firstValueFrom(
                this.apiService.getMessages(conversationId)
            );
            this.messagesSubject.next(messages);
        } catch (error) {
            console.error('Errore durante il caricamento dei messaggi:', error);
            this.messagesSubject.next([]);
        }
    }

    async sendMessage(content: string): Promise<void> {
        if (!content.trim()) return;
        
        const activeConversation = this.activeConversationSubject.getValue();
        if (!activeConversation) return;
        
        const userMessage: Message = {
            message_id: Date.now(),
            conversation_id: activeConversation.conversation_id,
            sender: 'user',
            content: content,
            created_at: new Date().toISOString()
        };
        
        const currentMessages = this.messagesSubject.getValue();
        this.messagesSubject.next([...currentMessages, userMessage]);
        
        this.isWaitingResponse = true;
        
        try {
            await firstValueFrom(
                this.apiService.sendMessage(activeConversation.conversation_id, content)
            );
            this.loadMessages(activeConversation.conversation_id);
        } catch (error) {
            console.error('Errore durante l\'invio del messaggio:', error);
        } finally {
            this.isWaitingResponse = false;
        }
    }

    async deleteConversation(conversationId: string): Promise<void> {
        if (!this.currentSessionId) return;
        
        const conversations = this.conversationsSubject.value;
        const activeConversation = this.activeConversationSubject.value;
        
        try {
            await firstValueFrom(
                this.apiService.deleteConversation(conversationId)
            );
            
            const updatedConversations = conversations.filter(c => c.conversation_id !== conversationId);
            this.conversationsSubject.next(updatedConversations);
            
            if (activeConversation && activeConversation.conversation_id === conversationId) {
                if (updatedConversations.length > 0) {
                    this.setActiveConversation(updatedConversations[0]);
                } else {
                    await this.createConversation();
                }
            }
        } catch (error) {
            console.error('Errore durante l\'eliminazione della conversazione:', error);
        }
    }

    async sendFeedback(messageId: string, isPositive: boolean): Promise<void> {
        if (!this.currentSessionId) return;
        
        try {
            await firstValueFrom(
                this.apiService.sendFeedback(messageId, isPositive)
            );
        } catch (error) {
            console.error('Errore durante l\'invio del feedback:', error);
        }
    }
}

