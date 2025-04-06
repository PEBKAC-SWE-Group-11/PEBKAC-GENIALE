import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ChatService } from '../Shared/Services/Chat.service';
import { ApiService } from '../Shared/Services/Api.service';
import { firstValueFrom } from 'rxjs';
import { Conversation } from '../Shared/Models/Conversation.model';
import { Message } from '../Shared/Models/Message.model';
import { of } from 'rxjs';

describe('Chat.service', () => {
    let apiServiceMock = {
        createSession: jasmine.createSpy('createSession'),
        deleteConversation: jasmine.createSpy('deleteConversation'),
        createConversation: jasmine.createSpy('createConversation'),
        getMessages: jasmine.createSpy('getMessages'),
        updateSession: jasmine.createSpy('updateSession'),
        getConversations: jasmine.createSpy('getConversations'),
        sendMessage: jasmine.createSpy('sendMessage'),
        updateConversationTimestamp: jasmine.createSpy('updateConversationTimestamp'),
        sendFeedback: jasmine.createSpy('sendFeedback'),
        askQuestion: jasmine.createSpy('askQuestion'),
        readSession: jasmine.createSpy('readSession'),
    };

    let chatService: ChatService;
    let httpMock: HttpTestingController;
    
    beforeEach(() =>{
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [ChatService, { provide: ApiService, useValue: apiServiceMock }],
        });

        httpMock = TestBed.inject(HttpTestingController);
        localStorage.clear();
        
        // Reset delle spy
        Object.values(apiServiceMock).forEach(spy => spy.calls.reset());
    });

    async function setup(): Promise<ChatService> {
        const sessionIdMock = '12345'
        const sessionMock = { sessionId: sessionIdMock };
        const conversationId = '0'
        const conversationMock = { conversationId: conversationId };
        const conversationArray: Conversation[] = [];
        conversationArray.push({
            conversationId: conversationId,    
            sessionId: sessionIdMock,
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test1'
        });

        const mex = {
            messageId: '0',
            conversationId: conversationId,
            sender: 'user',
            content: 'ciao',
            createdAt: new Date().toISOString
        };

        apiServiceMock.createSession.and.returnValue(of(sessionMock));
        apiServiceMock.deleteConversation.and.returnValue(of(null));
        apiServiceMock.createConversation.and.returnValue(of(conversationMock));
        apiServiceMock.getConversations.and.returnValue(of(conversationArray));
        apiServiceMock.getMessages.and.returnValue(of(mex));

        chatService = TestBed.inject(ChatService);
        await new Promise(resolve => setTimeout(resolve, 0));

        return chatService;
    }

    it('should test setup', async() => {
        const service = await setup();

        expect(service).toBeTruthy();
        expect(localStorage.getItem('sessionId')).toEqual('12345');
        expect((await firstValueFrom(service.conversations$)).length).toEqual(1);
    });

    it('should update a session', async() => {
        const sessionIdMock = '12345';
        const sessionMock = { sessionId: sessionIdMock };
        const updateSessionMock = { sessionId: sessionIdMock, isActive: true}
        const conversationMock = { conversationId: '1' };
        localStorage.setItem('sessionId', sessionIdMock);
        const conversationsMock: Conversation[] = [];

        apiServiceMock.createSession.and.returnValue(of(sessionMock));
        apiServiceMock.updateSession.and.returnValue(of({ success: true }))
        apiServiceMock.createConversation.and.returnValue(of(conversationMock));
        apiServiceMock.deleteConversation.and.returnValue(of(null));
        apiServiceMock.getConversations.and.returnValue(of(conversationsMock));
        apiServiceMock.readSession.and.returnValue(of(updateSessionMock));

        chatService = TestBed.inject(ChatService);
        await new Promise(resolve => setTimeout(resolve, 0));

        expect(apiServiceMock.updateSession).toHaveBeenCalled();
    });

    it('should load old conversations', async() => {
        const sessionIdMock = '12345';
        const sessionMock = { sessionId: sessionIdMock };
        const conversationsMock: Conversation[] = [];

            conversationsMock.push({
                conversationId: '1',
                sessionId: sessionIdMock,
                createdAt: '',
                updatedAt: '',
                toDelete: false,
                title: 'test1'
            })

            conversationsMock.push({
                conversationId: '2',
                sessionId: sessionIdMock,
                createdAt: '',
                updatedAt: '',
                toDelete: false,
                title: 'test2'
            })

            conversationsMock.push({
                conversationId: '3',
                sessionId: sessionIdMock,
                createdAt: '',
                updatedAt: '',
                toDelete: false,
                title: 'test3'
            })

        apiServiceMock.createSession.and.returnValue(of(sessionMock));
        apiServiceMock.updateSession.and.returnValue(of({ success: true }))
        apiServiceMock.deleteConversation.and.returnValue(of(null));
        apiServiceMock.getConversations.and.returnValue(of(conversationsMock))

        chatService = TestBed.inject(ChatService);
        await new Promise(resolve => setTimeout(resolve, 0));

        const promise = await firstValueFrom(chatService.conversations$);

        expect(promise.length).toEqual(3);
        expect(promise[0]).toEqual({
            conversationId: '1',
            sessionId: sessionIdMock,
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test1'
        });

        expect(promise[1]).toEqual({
            conversationId: '2',
            sessionId: sessionIdMock,
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test2'
        });

        expect(promise[2]).toEqual({
            conversationId: '3',
            sessionId: sessionIdMock,
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test3'
        });
    });

    it('should not create a conversation without a session', async() => {
        localStorage.clear();
        chatService = TestBed.inject(ChatService);
        let promise = await chatService.createConversation();
        expect(promise).toBe(null);
    });

    it('should create a conversation', async() => {
        const sessionIdMock = '12345'
        const sessionMock = { sessionId: sessionIdMock };
        const conversationId = '0';
        const conversationMock = { conversationId: conversationId };

        apiServiceMock.createSession.and.returnValue(of(sessionMock));
        apiServiceMock.createConversation.and.returnValue(of(conversationMock));

        chatService = TestBed.inject(ChatService);
        await new Promise(resolve => setTimeout(resolve, 0));
        await chatService.createConversation();
        
        const response = firstValueFrom(chatService.conversations$);
        const promise = await response;
        
        console.log('Conversation promise:', JSON.stringify(promise));
        console.log('Conversation title:', promise[0].title);
        console.log('Expected title:', `test1`);

        expect(promise[0].conversationId).toEqual(conversationId);
        expect(promise[0].sessionId).toEqual(sessionIdMock);
        expect(promise[0].title).toEqual(`test1`);
    });

    it('should not send a message', async() => {
        const chatService = await setup();
        const messageResponse = await chatService.sendMessage('');
        expect(messageResponse).toBeUndefined();
    });

    it('should delete a (not active) conversation', async() => {
        const chatService = await setup();
        const conversationId = '1';
        const conversationMock = { conversationId: conversationId };
        const convArray: Conversation[] = [];
        convArray.push({
            conversationId: '1',
            sessionId: '12345',
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test1'
        });

        convArray.push({
            conversationId: '0',
            sessionId: '12345',
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test0'
        });

        apiServiceMock.createConversation.and.returnValue(of(conversationMock));
        apiServiceMock.getConversations.and.returnValue(of(convArray));
        await chatService.createConversation();
        expect((await firstValueFrom(chatService.conversations$)).length).toEqual(2);

        apiServiceMock.deleteConversation.and.returnValue(of(null));
        await chatService.deleteConversation('0');

        expect((await firstValueFrom(chatService.conversations$)).length).toEqual(1);
    });

    it('should not delete a conversation without session', async() => {
        const chatService = await setup();
        localStorage.clear();

        const response = await chatService.deleteConversation('1');
        expect(response).toBeUndefined();
    });

    it('should not send a message without session', async() => {
        const chatService = await setup();
        localStorage.clear();

        const response = await chatService.sendMessage('test');
        expect(response).toBeUndefined();
    });

    it('should send a message', async() => {
        const chatService = await setup();
        const messageId = '0';
        const messageMock = { messageId: messageId };

        apiServiceMock.sendMessage.and.returnValue(of(messageMock));
        await chatService.sendMessage('test');

        expect(apiServiceMock.sendMessage).toHaveBeenCalled();
    });

    it('should reach the conversation limit', async() => {
        const chatService = await setup();
        const conversationsMock: Conversation[] = [];

        for (let i = 0; i < 10; i++) {
            conversationsMock.push({
                conversationId: i.toString(),
                sessionId: '12345',
                createdAt: '',
                updatedAt: '',
                toDelete: false
            });
        }

        apiServiceMock.getConversations.and.returnValue(of(conversationsMock));
        
        // Trigger a reload to ensure the conversations are updated
        await chatService['reloadConversations']();
        
        // Verifica che le conversazioni siano state aggiornate correttamente
        const conversationsLength = (await firstValueFrom(chatService.conversations$)).length;
        expect(conversationsLength).toBe(10);
        
        const hasReached = chatService.hasReachedConversationLimit();
        expect(hasReached).toBe(true);
    });

    it('should send a feedback', async() => {
        const chatService = await setup();
        const feedbackIdMock = '0';
        const feedbackMock = { feedbackId: feedbackIdMock };

        apiServiceMock.sendFeedback.and.returnValue(of(feedbackMock));
        await chatService.sendFeedback('0', true, 'test');

        expect(apiServiceMock.sendFeedback).toHaveBeenCalled();
    });

    it('should not send a feedback without session', async() => {
        const chatService = await setup();
        localStorage.clear();

        const response = await chatService.sendFeedback('0', true, 'test');
        expect(response).toBeUndefined();
    });
});