import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, firstValueFrom } from 'rxjs';
import { Message } from '../models/message.model';
import { Conversation } from '../models/conversation.model';
import { ApiService } from './api.service';

@Injectable({
    providedIn: 'root'
})

export class ChatService {
    private conversationsSubject = new BehaviorSubject<Conversation[]>([]);
    private activeConversationSubject = new BehaviorSubject<Conversation | null>(null);
    private messagesSubject = new BehaviorSubject<Message[]>([]);
    
    private readonly MAX_CONVERSATIONS = 10;
    private readonly MAX_MESSAGE_LENGTH = 500;
    private sessionId: string | null = null;

    constructor(private apiService: ApiService) {
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
        this.sessionId = localStorage.getItem('sessionId');
        
        if (this.sessionId) {
            await this.loadConversations(this.sessionId);
        } else {
            await this.createNewSession();
        }
    }

    private async createNewSession(): Promise<void> {
        try {
            const response = await firstValueFrom(this.apiService.createSession());
            this.sessionId = response.sessionId;
            localStorage.setItem('sessionId', this.sessionId);
            
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

    async createConversation(): Promise<void> {
        if (!this.sessionId) return;
        
        const conversations = this.conversationsSubject.value;
        
        if (conversations.length >= this.MAX_CONVERSATIONS) {
            throw new Error(`Hai raggiunto il limite massimo di ${this.MAX_CONVERSATIONS} conversazioni.`);
        }
        
        try {
            const newConversation = await firstValueFrom(
                this.apiService.createConversation(this.sessionId)
            );
            
            const updatedConversations = [...conversations, newConversation];
            this.conversationsSubject.next(updatedConversations);
            this.setActiveConversation(newConversation);
        } catch (error) {
            console.error('Errore durante la creazione della conversazione:', error);
        }
    }

    setActiveConversation(conversation: Conversation): void {
        this.activeConversationSubject.next(conversation);
        this.loadMessages(conversation.id);
    }

    private async loadMessages(conversationId: string): Promise<void> {
        if (!this.sessionId) return;
        
        try {
            const messages = await firstValueFrom(
                this.apiService.getMessages(this.sessionId, conversationId)
            );
            this.messagesSubject.next(messages);
        } catch (error) {
            console.error('Errore durante il caricamento dei messaggi:', error);
            this.messagesSubject.next([]);
        }
    }

    async sendMessage(content: string): Promise<void> {
        const activeConversation = this.activeConversationSubject.value;
        if (!this.sessionId || !activeConversation) return;
        
        if (content.length > this.MAX_MESSAGE_LENGTH) {
            throw new Error(`Il messaggio non può superare i ${this.MAX_MESSAGE_LENGTH} caratteri.`);
        }
        
        try {
            const response = await firstValueFrom(
                this.apiService.sendMessage(this.sessionId, activeConversation.id, content)
            );
            
            await this.loadMessages(activeConversation.id);
        } catch (error) {
            console.error('Errore durante l\'invio del messaggio:', error);
        }
    }

    async deleteConversation(conversationId: string): Promise<void> {
        if (!this.sessionId) return;
        
        const conversations = this.conversationsSubject.value;
        const activeConversation = this.activeConversationSubject.value;
        
        try {
            await firstValueFrom(
                this.apiService.deleteConversation(this.sessionId, conversationId)
            );
            
            const updatedConversations = conversations.filter(c => c.id !== conversationId);
            this.conversationsSubject.next(updatedConversations);
            
            if (activeConversation && activeConversation.id === conversationId) {
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
        if (!this.sessionId) return;
        
        try {
            await firstValueFrom(
                this.apiService.sendFeedback(this.sessionId, messageId, isPositive)
            );
        } catch (error) {
            console.error('Errore durante l\'invio del feedback:', error);
        }
    }
}

