import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, firstValueFrom } from 'rxjs';
import { Message } from '../models/Message.model';
import { Conversation } from '../models/Conversation.model';
import { ApiService } from './Api.service';

@Injectable({
    providedIn: 'root'
})

export class ChatService {
    private conversationsSubject = new BehaviorSubject<Conversation[]>([]);
    private activeConversationSubject = new BehaviorSubject<Conversation | null>(null);
    private messagesSubject = new BehaviorSubject<Message[]>([]);
    private currentSessionId: string = ''; 
    private readonly MAX_CONVERSATIONS = 10;
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
    
    get isWaitingForResponse(): boolean {
        return this.isWaitingResponse;
    }

    private async initializeFromStorage(): Promise<void> {
        this.currentSessionId = localStorage.getItem('sessionId') || '';
        
        if (this.currentSessionId != '' && this.currentSessionId != null) {
            const session = await firstValueFrom(this.apiService.readSession(this.currentSessionId));
            if (!session.isActive) {
                console.log('La sessione non è attiva, creando una nuova sessione.');
                localStorage.removeItem('sessionId');
                await this.createNewSession();
                return;
            }
            try {
                await firstValueFrom(this.apiService.updateSession(this.currentSessionId));
                console.log('Sessione aggiornata con successo');
            } catch (error) {
                console.error('Errore nell\'aggiornamento della sessione:', error);
            }            
            await this.loadConversations(this.currentSessionId);
        } else {
            await this.createNewSession();
        }
    }

    private async createNewSession(): Promise<void> {
        try {
            const response = await firstValueFrom(this.apiService.createSession());
            this.currentSessionId = response.sessionId;
            localStorage.setItem('sessionId', this.currentSessionId);
            await this.createConversation();
        } catch (error) {
            console.error('Errore durante la creazione della sessione:', error);
        }
    }

    private async loadConversations(sessionId: string): Promise<void> {
        try {
            const conversations = await firstValueFrom(this.apiService.getConversations(sessionId));
            console.log('Conversazioni ricevute dal server:', JSON.stringify(conversations));
            this.conversationsSubject.next(conversations);            
            if (conversations.length > 0) {
                console.log('Prima conversazione:', conversations[0]);
                this.setActiveConversation(conversations[0]);
            } else {
                await this.createConversation();
            }
        } catch (error) {
            console.error('Errore durante il caricamento delle conversazioni:', error);
            if (error && typeof error === 'object' && 'status' in error && error.status === 500) {
                console.log('Tentativo di creazione di una nuova sessione dopo errore 500');
                await this.createNewSession();
            } else {
                await this.createNewSession();
            }
        }
    }

    async createConversation(): Promise<Conversation | null> {
        if (!this.currentSessionId) return null;        
        await this.enforceConversationLimit();
        try {
            await firstValueFrom(
                this.apiService.createConversation(this.currentSessionId)
            );
            const conversations = await firstValueFrom(
                this.apiService.getConversations(this.currentSessionId)
            );
            this.conversationsSubject.next(conversations);
            if (conversations.length > 0) {
                this.setActiveConversation(conversations[0]);
                return conversations[0];
            }
            return null;
        } catch (error) {
            console.error('Errore durante la creazione della conversazione:', error);
            throw error;
        }
    }
    
    private async enforceConversationLimit(): Promise<void> {
        const currentConversations = this.conversationsSubject.getValue();
        if (currentConversations.length < this.MAX_CONVERSATIONS) return;
        try {
            const oldestConversation = currentConversations[currentConversations.length - 1];
            await firstValueFrom(this.apiService.deleteConversation(oldestConversation.conversationId));
        } catch (error) {
            console.error('Errore durante l\'eliminazione della conversazione più vecchia:', error);
        }
    }

    setActiveConversation(conversation: Conversation): void {
        this.activeConversationSubject.next(conversation);
        this.loadMessages(conversation.conversationId);
    }

    async loadMessages(conversationId?: string): Promise<void> {
        if (!conversationId) {
            const activeConversation = this.activeConversationSubject.getValue();
            if (!activeConversation) return;
            conversationId = activeConversation.conversationId;
        }
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
        this.isWaitingResponse = true;
        try {
            await firstValueFrom(
                this.apiService.sendMessage(activeConversation.conversationId, content)
            );
            await this.loadMessages(activeConversation.conversationId);
            await this.reloadConversations();
            await firstValueFrom(
                this.apiService.askQuestion(activeConversation.conversationId, content)
            );
            await this.loadMessages(activeConversation.conversationId);
            await this.reloadConversations();
        } catch (error) {
            console.error('Errore durante l\'invio del messaggio:', error);
        } finally {
            this.isWaitingResponse = false;
        }
    }

    private async reloadConversations(): Promise<void> {
        if (!this.currentSessionId) return;
        try {
            const conversations = await firstValueFrom(
                this.apiService.getConversations(this.currentSessionId)
            );
            this.conversationsSubject.next(conversations);
            const activeConversation = this.activeConversationSubject.getValue();
            if (activeConversation) {
                const updatedActiveConversation = conversations.find(
                    (c: Conversation) => c.conversationId === activeConversation.conversationId
                );
                
                if (updatedActiveConversation) {
                    this.activeConversationSubject.next(updatedActiveConversation);
                }
            }
        } catch (error) {
            console.error('Errore durante il recupero delle conversazioni:', error);
        }
    }

    async deleteConversation(conversationId: string): Promise<void> {
        if (!this.currentSessionId) return;
        const conversations = this.conversationsSubject.value;
        const activeConversation = this.activeConversationSubject.value;
        const isActiveConversation = activeConversation?.conversationId === conversationId;
        
        try {
            await firstValueFrom(
                this.apiService.deleteConversation(conversationId)
            );
            
            const updatedConversations = conversations.filter((c: Conversation) => c.conversationId !== conversationId);
            this.conversationsSubject.next(updatedConversations);
            
            if (isActiveConversation) {
                await this.createConversation();
            }
        } catch (error) {
            console.error('Errore durante l\'eliminazione della conversazione:', error);
        }
    }

    async sendFeedback(messageId: string, isPositive: boolean, content?: string): Promise<void> {
        try {
            await firstValueFrom(
                this.apiService.sendFeedback(messageId, isPositive, content)
            );
            const activeConversation = this.activeConversationSubject.getValue();
            if (activeConversation) {
                this.loadMessages(activeConversation.conversationId);
            }
        } catch (error) {
            console.error('Errore durante l\'invio del feedback:', error);
        }
    }

    hasReachedConversationLimit(): boolean {
        return this.conversationsSubject.getValue().length >= this.MAX_CONVERSATIONS;
    }
}

