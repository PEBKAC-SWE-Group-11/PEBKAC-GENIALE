import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ChatService } from '../shared/services/chat.service';
import { ApiService } from '../shared/services/api.service';
import { firstValueFrom } from 'rxjs';
import { Conversation } from '../shared/models/conversation.model';
import { Message } from '../shared/models/message.model';
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
        readSession: jest.fn(),
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
        }

        apiServiceMock.createSession.mockReturnValue(of(sessionMock));
        apiServiceMock.deleteConversation.mockReturnValue(of(null));
        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));
        apiServiceMock.getConversations.mockReturnValue(of(conversationArray))
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
        const sessionMock = { sessionId: sessionIdMock };
        const updateSessionMock = { sessionId: sessionIdMock, isActive: true}
        const conversationMock = { conversationId: '1' };
        localStorage.setItem('sessionId', sessionIdMock);
        const conversationsMock: Conversation[] = [];

        apiServiceMock.createSession.mockReturnValue(of(sessionMock));
        apiServiceMock.updateSession.mockReturnValue(of({ success: true }))
        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));
        apiServiceMock.deleteConversation.mockReturnValue(null);
        apiServiceMock.getConversations.mockReturnValue(of(conversationsMock));
        apiServiceMock.readSession.mockReturnValue(of(updateSessionMock));

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

        apiServiceMock.createSession.mockReturnValue(of(sessionMock));
        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));

        chatService = TestBed.inject(ChatService);
        await new Promise(resolve => setTimeout(resolve, 0));
        await chatService.createConversation();
        
        const response = firstValueFrom(chatService.conversations$);
        const promise = await response;

        expect(promise[0].conversationId).toEqual(conversationId);
        expect(promise[0].sessionId).toEqual(sessionIdMock);
        expect(promise[0].title).toEqual(`test${conversationId}`);
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
        })

        apiServiceMock.createConversation.mockReturnValue(of(conversationMock));
        apiServiceMock.getConversations.mockReturnValue(of(convArray));
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
        const convArray: Conversation[] = [];

        for(let i = 0; i<10; ++i){
            const conversationMock = { conversationId: i }
            apiServiceMock.createConversation.mockReturnValue(of(conversationMock))
            convArray.push({
                conversationId: i.toString(),    
                sessionId: '12345',
                createdAt: '',
                updatedAt: '',
                toDelete: false,
                title: ''
            })
            apiServiceMock.getConversations.mockReturnValue(of(convArray));
            await chatService.createConversation();
        }

        const promise = await firstValueFrom(chatService.conversations$);

        const response = chatService.hasReachedConversationLimit();
        expect(response).toEqual(true);
    });

    it('should send a message', async() => {
        const messageMock = { messageId: '1' };
        const messageArray: Message[] = [];
        messageArray.push({
            messageId: '0',
            conversationId: '0',
            sender: 'user',
            content: 'test',
            createdAt: new Date().toISOString()
        });

        messageArray.push({
            messageId: '1',
            conversationId: '0',
            sender: 'user',
            content: 'test',
            createdAt: new Date().toISOString()
        });

        const conversationArray: Conversation[] = [];
        conversationArray.push({
            conversationId: '0',    
            sessionId: '12345',
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test1'
        });

        const chatService = await setup();
        const activeConversation = await firstValueFrom(chatService.activeConversation$);
        expect(activeConversation?.conversationId).toEqual('0');

        const isWaitingResponse = chatService.isWaitingForResponse;
        expect(isWaitingResponse).toEqual(false);

        apiServiceMock.sendMessage.mockReturnValue(of(messageMock));
        apiServiceMock.askQuestion.mockReturnValue(of(messageMock));
        apiServiceMock.getMessages.mockReturnValue(of(messageArray));
        apiServiceMock.getConversations.mockReturnValue(of(conversationArray));
        await chatService.sendMessage('test');

        const messages = await firstValueFrom(chatService.messages$);
        expect(messages.length).toEqual(2);
        expect(messages[1].messageId).toEqual('1');
        expect(messages[1].conversationId).toEqual('0');
        expect(messages[1].content).toEqual('test');
    });

});