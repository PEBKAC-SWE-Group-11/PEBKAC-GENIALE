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
        this.currentSessionId = localStorage.getItem('session_id') || '';
        
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
            // Trova la conversazione con l'updated_at più vecchio
            // (ora che le conversazioni sono ordinate per updated_at, dovrebbe essere l'ultima)
            const oldestConversation = currentConversations[currentConversations.length - 1];
            
            try {
                await firstValueFrom(
                    this.apiService.deleteConversation(oldestConversation.conversation_id)
                );
                
                const updatedConversations = currentConversations.filter(
                    c => c.conversation_id !== oldestConversation.conversation_id
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
            
            if (response && response.conversation_id) {
                const newConversation = {
                    conversation_id: response.conversation_id,
                    session_id: this.currentSessionId,
                    created_at: new Date().toISOString(),
                    title: `Conversazione ${response.conversation_id}`,
                    updated_at: new Date().toISOString(),
                    to_delete: false
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
            message_id: Date.now().toString(),
            conversation_id: activeConversation.conversation_id,
            sender: 'user',
            content: content,
            created_at: new Date().toISOString()
        };
        
        const currentMessages = this.messagesSubject.getValue();
        this.messagesSubject.next([...currentMessages, userMessage]);
        
        this.isWaitingResponse = true;
        
        try {
            // Invia il messaggio al backend
            await firstValueFrom(
                this.apiService.sendMessage(activeConversation.conversation_id, content)
            );
            
            // Aggiorna il timestamp della conversazione
            await firstValueFrom(
                this.apiService.updateConversationTimestamp(activeConversation.conversation_id)
            );
            
            // Aggiorna localmente l'ordine delle conversazioni
            this.updateConversationOrder(activeConversation.conversation_id);
            
            // Ricarica i messaggi della conversazione
            this.loadMessages(activeConversation.conversation_id);
        } catch (error) {
            console.error('Errore durante l\'invio del messaggio:', error);
        } finally {
            this.isWaitingResponse = false;
        }
    }

    // Nuovo metodo per aggiornare l'ordine delle conversazioni localmente
    private updateConversationOrder(conversationId: string): void {
        const conversations = this.conversationsSubject.getValue();
        const conversation = conversations.find(c => c.conversation_id === conversationId);
        
        if (conversation) {
            // Aggiorna il timestamp
            conversation.updated_at = new Date().toISOString();
            
            // Rimuovi la conversazione dalla lista
            const remainingConversations = conversations.filter(
                c => c.conversation_id !== conversationId
            );
            
            // Aggiungi la conversazione in cima alla lista
            this.conversationsSubject.next([conversation, ...remainingConversations]);
        }
    }

    async deleteConversation(conversationId: string): Promise<void> {
        if (!this.currentSessionId) return;
        
        const conversations = this.conversationsSubject.value;
        const activeConversation = this.activeConversationSubject.value;
        const isActiveConversation = activeConversation?.conversation_id === conversationId;
        
        try {
            // L'API service rimane uguale ma nel backend è un soft delete
            await firstValueFrom(
                this.apiService.deleteConversation(conversationId)
            );
            
            // L'interfaccia utente rimuove la conversazione dalla lista (come prima)
            const updatedConversations = conversations.filter(c => c.conversation_id !== conversationId);
            this.conversationsSubject.next(updatedConversations);
            
            if (isActiveConversation) {
                await this.createConversation();
            }
        } catch (error) {
            console.error('Errore durante l\'eliminazione della conversazione:', error);
        }
    }

    async sendFeedback(messageId: string, isPositive: boolean, content?: string): Promise<void> {
        if (!this.currentSessionId) return;
        
        try {
            await firstValueFrom(
                this.apiService.sendFeedback(messageId, isPositive, content)
            );
            
            // Aggiorna localmente il feedback
            const currentMessages = this.messagesSubject.getValue();
            const updatedMessages = currentMessages.map(message => {
                if (message.message_id === messageId) {
                    // Usa cast esplicito per evitare errori di tipizzazione
                    return {
                        ...message,
                        feedback: {
                            feedback_id: `temp_${Date.now()}`, // ID temporaneo fino al refresh
                            message_id: messageId,
                            type: isPositive ? 'positive' : 'negative',
                            content: content || undefined,
                            created_at: new Date().toISOString()
                        } as Feedback
                    } as Message;
                }
                return message;
            });
            
            // Usa cast esplicito anche qui
            this.messagesSubject.next(updatedMessages as Message[]);
            
            // Ricarica i messaggi dal server
            const activeConversation = this.activeConversationSubject.getValue();
            if (activeConversation) {
                await this.loadMessages(activeConversation.conversation_id);
            }
        } catch (error) {
            console.error('Errore durante l\'invio del feedback:', error);
        }
    }

    // Aggiungiamo un metodo di utilità per verificare se il limite è stato raggiunto
    hasReachedConversationLimit(): boolean {
        return this.conversationsSubject.getValue().length >= this.MAX_CONVERSATIONS;
    }
}

