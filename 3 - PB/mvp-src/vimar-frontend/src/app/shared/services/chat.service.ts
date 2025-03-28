import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, firstValueFrom } from 'rxjs';
import { Message } from '../models/message.model';
import { Conversation } from '../models/conversation.model';
import { ApiService } from './api.service';
import { Session } from '../models/session.model';
import { Feedback } from '../models/feedback.model';

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
        this.currentSessionId = localStorage.getItem('sessionId') || '';
        
        if (this.currentSessionId != '' && this.currentSessionId != null) {
            // Aggiorna il timestamp della sessione all'avvio dell'app
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
        
        // Gestione del limite massimo di conversazioni
        const currentConversations = this.conversationsSubject.getValue();
        if (currentConversations.length >= this.MAX_CONVERSATIONS) {
            // Trova la conversazione con l'updatedAt più vecchio
            // (ora che le conversazioni sono ordinate per updatedAt, dovrebbe essere l'ultima)
            const oldestConversation = currentConversations[currentConversations.length - 1];
            
            try {
                await firstValueFrom(
                    this.apiService.deleteConversation(oldestConversation.conversationId)
                );
                
                const updatedConversations = currentConversations.filter(
                    c => c.conversationId !== oldestConversation.conversationId
                );
                this.conversationsSubject.next(updatedConversations);
            } catch (error) {
                console.error('Errore durante l\'eliminazione della conversazione più vecchia:', error);
            }
        }
        
        // Procedi con la creazione della nuova conversazione
        try {
            const response = await firstValueFrom(
                this.apiService.createConversation(this.currentSessionId)
            );
            
            if (response && response.conversationId) {
                const newConversation = {
                    conversationId: response.conversationId,
                    sessionId: this.currentSessionId,
                    createdAt: new Date().toISOString(),
                    title: `Conversazione ${response.conversationId}`,
                    updatedAt: new Date().toISOString(),
                    toDelete: false
                } as Conversation;
                
                // Aggiungi la nuova conversazione in cima alla lista
                const updatedConversations = [
                    newConversation, 
                    ...this.conversationsSubject.getValue()
                ];
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
        this.loadMessages(conversation.conversationId);
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
            messageId: Date.now().toString(),
            conversationId: activeConversation.conversationId,
            sender: 'user',
            content: content,
            createdAt: new Date().toISOString()
        };
        
        const currentMessages = this.messagesSubject.getValue();
        this.messagesSubject.next([...currentMessages, userMessage]);
        
        this.isWaitingResponse = true;
        
        try {
            // Invia il messaggio dell'utente al backend
            await firstValueFrom(
                this.apiService.sendMessage(activeConversation.conversationId, content)
            );
            
            // Chiedi una risposta al modello LLM
            await firstValueFrom(
                this.apiService.askQuestion(activeConversation.conversationId, content)
            );
            
            // Aggiorna il timestamp della conversazione
            await firstValueFrom(
                this.apiService.updateConversationTimestamp(activeConversation.conversationId)
            );
            
            // Aggiorna localmente l'ordine delle conversazioni
            this.updateConversationOrder(activeConversation.conversationId);
            
            // Ricarica i messaggi della conversazione per ottenere sia il messaggio dell'utente che la risposta
            this.loadMessages(activeConversation.conversationId);
        } catch (error) {
            console.error('Errore durante l\'invio del messaggio:', error);
        } finally {
            this.isWaitingResponse = false;
        }
    }

    // Nuovo metodo per aggiornare l'ordine delle conversazioni localmente
    private updateConversationOrder(conversationId: string): void {
        const conversations = this.conversationsSubject.getValue();
        const conversation = conversations.find(c => c.conversationId === conversationId);
        
        if (conversation) {
            // Aggiorna il timestamp
            conversation.updatedAt = new Date().toISOString();
            
            // Rimuovi la conversazione dalla lista
            const remainingConversations = conversations.filter(
                c => c.conversationId !== conversationId
            );
            
            // Aggiungi la conversazione in cima alla lista
            this.conversationsSubject.next([conversation, ...remainingConversations]);
        }
    }

    async deleteConversation(conversationId: string): Promise<void> {
        if (!this.currentSessionId) return;
        
        const conversations = this.conversationsSubject.value;
        const activeConversation = this.activeConversationSubject.value;
        const isActiveConversation = activeConversation?.conversationId === conversationId;
        
        try {
            // L'API service rimane uguale ma nel backend è un soft delete
            await firstValueFrom(
                this.apiService.deleteConversation(conversationId)
            );
            
            // L'interfaccia utente rimuove la conversazione dalla lista (come prima)
            const updatedConversations = conversations.filter(c => c.conversationId !== conversationId);
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
            
            // Aggiorna il messaggio nella lista locale
            const currentMessages = this.messagesSubject.getValue();
            const messageIndex = currentMessages.findIndex(m => m.messageId === messageId);
            
            if (messageIndex !== -1) {
                const updatedMessages = [...currentMessages];
                const message = updatedMessages[messageIndex];
                
                // Crea l'oggetto di feedback
                const feedback: Feedback = {
                    feedbackId: Date.now().toString(), // ID temporaneo, verrà sostituito quando ricaricheremo i messaggi
                    messageId: messageId,
                    type: isPositive ? 'positive' : 'negative',
                    content: content || null,
                    createdAt: new Date().toISOString()
                };
                
                // Aggiorna il messaggio con il nuovo feedback
                updatedMessages[messageIndex] = {
                    ...message,
                    feedback
                };
                
                // Aggiorna lo stato
                this.messagesSubject.next(updatedMessages);
            }
        } catch (error) {
            console.error('Errore durante l\'invio del feedback:', error);
        }
    }

    hasReachedConversationLimit(): boolean {
        return this.conversationsSubject.getValue().length >= this.MAX_CONVERSATIONS;
    }
}

