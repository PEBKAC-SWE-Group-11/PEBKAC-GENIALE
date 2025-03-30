import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ChatService } from '../shared/services/chat.service';
import { ApiService } from '../shared/services/api.service';
import { firstValueFrom } from 'rxjs';
import { Conversation } from '../shared/models/conversation.model';
import { environment } from '../../environments/environment';
import { of } from 'rxjs';

describe('chat.service', () => {
    let apiServiceMock = {
        createSession: jest.fn(),
        deleteConversation: jest.fn(),
        createConversation: jest.fn(),
        getMessages: jest.fn(),
        updateSession: jest.fn(),
        getConversations: jest.fn(),
        sendMessage: jest.fn(),
        updateConversationTimestamp: jest.fn(),
        sendFeedback: jest.fn(),
        askQuestion: jest.fn(),
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
    });

    async function setup(): Promise<ChatService> {
        const sessionIdMock = '12345'
        const sessionMock = { sessionId: sessionIdMock };
        const conversationId = '0'
        const conversationMock = { conversationId: conversationId };
        const mex = {
            messageId: '1',
            conversationId: conversationId,
            sender: 'user',
            content: 'ciao',
            createdAt: new Date().toISOString
        }

        apiServiceMock.createSession.mockReturnValue(of(sessionMock));
        apiServiceMock.deleteConversation.mockReturnValue(of(null));
        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));
        apiServiceMock.getMessages.mockReturnValue(of(mex));


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
        const updateSessionIdMock = '123456';
        const sessionMock = { sessionId: sessionIdMock };
        const conversationMock = { conversationId: '1' };
        localStorage.setItem('sessionId', sessionIdMock);
        const conversationsMock: Conversation[] = [];

        apiServiceMock.createSession.mockReturnValue(of(sessionMock));
        apiServiceMock.updateSession.mockReturnValue(of({ success: true }))
        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));
        apiServiceMock.deleteConversation.mockReturnValue(null);
        apiServiceMock.getConversations.mockReturnValue(of(conversationsMock))

        chatService = TestBed.inject(ChatService);
        await new Promise(resolve => setTimeout(resolve, 0));
    })

    it('should load old conversations', async() => {
        const sessionIdMock = '12345';
        const updateSessionIdMock = '123456';
        const sessionMock = { sessionId: sessionIdMock };
        localStorage.setItem('sessionId', sessionIdMock);
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

        apiServiceMock.createSession.mockReturnValue(of(sessionMock));
        apiServiceMock.updateSession.mockReturnValue(of({ success: true }))
        apiServiceMock.deleteConversation.mockReturnValue(null);
        apiServiceMock.getConversations.mockReturnValue(of(conversationsMock))

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
        })

        expect(promise[1]).toEqual({
            conversationId: '2',
            sessionId: sessionIdMock,
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test2'
        })

        expect(promise[2]).toEqual({
            conversationId: '3',
            sessionId: sessionIdMock,
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test3'
        })
    });

    it('should create a new conversation if there are not', async() => {
        const sessionIdMock = '12345';
        const updateSessionIdMock = '123456';
        const sessionMock = { sessionId: sessionIdMock };
        localStorage.setItem('sessionId', sessionIdMock);
        const conversationId = '1';
        const conversationMock = { conversationId: conversationId };
        const conversationsMock: Conversation[] = [];

        apiServiceMock.createSession.mockReturnValue(of(sessionMock));
        apiServiceMock.updateSession.mockReturnValue(of({ success: true }))
        apiServiceMock.deleteConversation.mockReturnValue(null);
        apiServiceMock.getConversations.mockReturnValue(of(conversationsMock));
        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));

        chatService = TestBed.inject(ChatService);
        await new Promise(resolve => setTimeout(resolve, 0));

        const promise = await firstValueFrom(chatService.conversations$);
        expect(promise.length).toBe(1);
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
        const conversationId = '1';
        const conversationMock = { conversationId: conversationId };
        
        const expectedConv = {
            conversationId: conversationId,
            sessionId: sessionIdMock,
            createdAt: new Date().toISOString(),
            title: `Conversazione ${conversationId}`,
            updatedAt: new Date().toISOString(),
            toDelete: false
        }

        apiServiceMock.createSession.mockReturnValue(of(sessionMock));
        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));

        chatService = TestBed.inject(ChatService);
        await new Promise(resolve => setTimeout(resolve, 0));
        const conv = await chatService.createConversation();
        
        const response = firstValueFrom(chatService.conversations$);
        const promise = await response;

        expect(conv?.conversationId).toEqual(conversationId);
        expect(conv?.sessionId).toEqual(sessionIdMock);
        expect(conv?.title).toEqual(`Conversazione ${conversationId}`);
    })

    it('should go beyond max number of conversations', async() => {    
        let conversationMock: { conversationId: String };
        const sessionIdMock = '12345'
        const conversationId = '10';
        const chatService = await setup();

        for(let i = 0; i<10; ++i){
            const conversationMock = { conversationId: i }
            apiServiceMock.createConversation.mockReturnValue(of(conversationMock))
            await chatService.createConversation();
        }

        /*const response = firstValueFrom(chatService.conversations$);
        const promise = await response;
        expect(promise.length).toEqual(10);*/

        conversationMock = { conversationId: conversationId };
        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));
        apiServiceMock.deleteConversation.mockReturnValue(of(true));
        await chatService.createConversation();

        const response = firstValueFrom(chatService.conversations$);
        const promise = await response;

        const lastConv = promise[0];

        expect(lastConv?.conversationId).toEqual(conversationId);
        expect(lastConv?.sessionId).toEqual(sessionIdMock);
        expect(lastConv?.title).toEqual(`Conversazione ${conversationId}`);
    });

    it('should check if the last conversation created is the newest', async() => {
        const sessionIdMock = '12345'
        const sessionMock = { sessionId: sessionIdMock };
        let conversationMock: { conversationId: String };
        
        apiServiceMock.createSession.mockReturnValue(of(sessionMock));

        chatService = TestBed.inject(ChatService);
        apiServiceMock.deleteConversation.mockReturnValue(of(true));
        await chatService.deleteConversation('1');

        for(let i = 1; i<=3; i++){
            conversationMock = { conversationId: i.toString() };
            apiServiceMock.createConversation.mockReturnValue(of(conversationMock));
            await chatService.createConversation();
            await new Promise(resolve => setTimeout(resolve, 10));
        }

        const response = firstValueFrom(chatService.conversations$);
        const promise = await response;

        expect(new Date(promise[0].updatedAt).getTime()).toBeGreaterThan(new Date(promise[1].updatedAt).getTime());
        expect(new Date(promise[1].updatedAt).getTime()).toBeGreaterThan(new Date(promise[2].updatedAt).getTime());
        expect(new Date(promise[0].updatedAt).getTime()).toBeGreaterThan(new Date(promise[2].updatedAt).getTime());        
    });

    /*it('should send a message', async() => {
        const chatService = await setup();
        const messageMock = {messageId: '2'};
        
        const promise = await firstValueFrom(chatService.messages$);

        apiServiceMock.sendMessage.mockReturnValue(of(messageMock));
        apiServiceMock.askQuestion.mockReturnValue(of())

        await chatService.sendMessage('test');

    })*/

    it('should not send a message', async() => {
        const chatService = await setup();
        const messageResponse = await chatService.sendMessage('');
        expect(messageResponse).toBeUndefined();
    });

    it('should delete a (not active) conversation', async() => {
        const chatService = await setup();
        const conversationId = '1';
        const conversationMock = { conversationId: conversationId };

        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));
        await chatService.createConversation();
        expect((await firstValueFrom(chatService.conversations$)).length).toEqual(2);

        apiServiceMock.deleteConversation.mockReturnValue(of(null));
        await chatService.deleteConversation('0');

        expect((await firstValueFrom(chatService.conversations$)).length).toEqual(1);
    });

    it('should not delete a conversation without session', async() => {
        const chatService = await setup();
        localStorage.clear();

        const response = await chatService.deleteConversation('1');
        expect(response).toBeUndefined();
    });

    it('should send a feedback', async() => {
        const chatService = await setup();

        apiServiceMock.sendFeedback.mockReturnValue(of({ message_id: '1' }))
        const feedbackMessage = await chatService.sendFeedback('1', true);

        const feedback = {
            messageId: '1',
            feedbackValue: 'positive',
            content: 'test',
        }

        const promise = await firstValueFrom(chatService.messages$);
        
        expect(apiServiceMock.sendFeedback).toHaveBeenCalled();
    });

    it('should not send a feedback without session', async() => {
        const chatService = await setup();
        localStorage.clear();
        const feedback = await chatService.sendFeedback('1', true);
        expect(feedback).toBeUndefined();
    });

    it('should reach the conversation limit', async() => {
        const MAX_CONVERSATIONS = 10;
        const chatService = await setup();
        for(let i = 0; i<10; ++i){
            const conversationMock = { conversationId: i }
            apiServiceMock.createConversation.mockReturnValue(of(conversationMock))
            await chatService.createConversation();
        }

        const promise = await firstValueFrom(chatService.conversations$);

        const response = chatService.hasReachedConversationLimit();
        expect(response).toEqual(true);
    })

});