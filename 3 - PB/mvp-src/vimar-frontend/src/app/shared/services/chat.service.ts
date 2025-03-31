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
    
    // Ripristiniamo la variabile globale per lo stato di attesa
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
    
    // Getter per verificare se l'applicazione è in attesa di una risposta
    get isWaitingForResponse(): boolean {
        return this.isWaitingResponse;
    }

    private async initializeFromStorage(): Promise<void> {
        this.currentSessionId = localStorage.getItem('sessionId') || '';
        
        if (this.currentSessionId != '' && this.currentSessionId != null) {
            // Controlla se la sessione è attiva
            const session = await firstValueFrom(this.apiService.readSession(this.currentSessionId));
            if (!session.isActive) {
                console.log('La sessione non è attiva, creando una nuova sessione.');
                localStorage.removeItem('sessionId');
                await this.createNewSession();
                return;
            }
            
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
        
        // Gestisci il limite in una funzione separata
        await this.enforceConversationLimit();
        
        try {
            // 1. Crea la conversazione nel backend
            await firstValueFrom(
                this.apiService.createConversation(this.currentSessionId)
            );
            
            // 2. Ricarica tutte le conversazioni dal backend
            const conversations = await firstValueFrom(
                this.apiService.getConversations(this.currentSessionId)
            );
            
            // 3. Aggiorna lo stato locale con i dati dal backend
            this.conversationsSubject.next(conversations);
            
            // 4. Imposta la nuova conversazione come attiva (dovrebbe essere la prima)
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
    
    // Metodo per gestire il limite massimo di conversazioni
    private async enforceConversationLimit(): Promise<void> {
        const currentConversations = this.conversationsSubject.getValue();
        
        if (currentConversations.length < this.MAX_CONVERSATIONS) return;
        
        // Elimina la conversazione più vecchia
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

    // Metodo per caricare i messaggi di una conversazione
    async loadMessages(conversationId?: string): Promise<void> {
        // Se non viene fornito un ID conversazione, usa quello attivo
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

    // Metodo per inviare un messaggio all'API e ottenere una risposta
    async sendMessage(content: string): Promise<void> {
        if (!content.trim()) return;
        
        const activeConversation = this.activeConversationSubject.getValue();
        if (!activeConversation) return;
        
        // Usa la variabile globale
        this.isWaitingResponse = true;
        
        try {
            // 1. Invia il messaggio dell'utente al backend
            await firstValueFrom(
                this.apiService.sendMessage(activeConversation.conversationId, content)
            );
            
            // 2. Ricarica i messaggi per visualizzare il messaggio dell'utente
            await this.loadMessages(activeConversation.conversationId);

            // 3. Ricarica tutte le conversazioni per ottenere l'ordine aggiornato dal backend
            await this.reloadConversations();
            
            // 4. Chiedi una risposta al modello LLM
            await firstValueFrom(
                this.apiService.askQuestion(activeConversation.conversationId, content)
            );
            
            // 5. Ricarica i messaggi per visualizzare la risposta
            await this.loadMessages(activeConversation.conversationId);
            
            // 6. Ricarica nuovamente le conversazioni per l'ordine aggiornato
            await this.reloadConversations();
        } catch (error) {
            console.error('Errore durante l\'invio del messaggio:', error);
        } finally {
            // Resetta la variabile globale
            this.isWaitingResponse = false;
        }
    }

    // Metodo per ricaricare tutte le conversazioni dal backend
    private async reloadConversations(): Promise<void> {
        if (!this.currentSessionId) return;
        
        try {
            // Recupera tutte le conversazioni dal backend (già ordinate per updatedAt)
            const conversations = await firstValueFrom(
                this.apiService.getConversations(this.currentSessionId)
            );
            
            // Aggiorna lo stato locale con le conversazioni ordinate dal backend
            this.conversationsSubject.next(conversations);
            
            // Mantieni attiva la conversazione corrente
            const activeConversation = this.activeConversationSubject.getValue();
            if (activeConversation) {
                // Trova la versione aggiornata della conversazione attiva
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
            // L'API service rimane uguale ma nel backend è un soft delete
            await firstValueFrom(
                this.apiService.deleteConversation(conversationId)
            );
            
            // L'interfaccia utente rimuove la conversazione dalla lista (come prima)
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
            
            // Ricarica i messaggi per aggiornare lo stato del feedback
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

