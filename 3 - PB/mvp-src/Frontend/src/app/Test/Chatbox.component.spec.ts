import { ChatboxComponent } from "../Core/Chatbox/Chatbox.component";
import { Message } from "../Shared/Models/Message.model";
import { Conversation } from "../Shared/Models/Conversation.model";
import { ChatService } from "../Shared/Services/Chat.service";
import { BehaviorSubject, firstValueFrom } from 'rxjs';
import { TestBed } from "@angular/core/testing";

describe('Chatbox.component', () => {
    let chatboxComponent: ChatboxComponent;

    const isWaitingForResponseValue = false;
    let chatServiceMock = {
        conversations$: new BehaviorSubject<Conversation[]>([]),
        activeConversation$: new BehaviorSubject<Conversation | null>(null),
        messages$: new BehaviorSubject<Message[]>([]),
        createConversation: jasmine.createSpy('createConversation').and.returnValue(Promise.resolve()),
        setActiveConversation: jasmine.createSpy('setActiveConversation'),
        loadMessages: jasmine.createSpy('loadMessages'),
        updateConversationTimestamp: jasmine.createSpy('updateConversationTimestamp'),
        sendMessage: jasmine.createSpy('sendMessage').and.returnValue(Promise.resolve()),
        updateConversationOrder: jasmine.createSpy('updateConversationOrder'),
        deleteConversation: jasmine.createSpy('deleteConversation'),
        sendFeedback: jasmine.createSpy('sendFeedback').and.returnValue(Promise.resolve()),
        hasReachedConversationLimit: jasmine.createSpy('hasReachedConversationLimit').and.returnValue(false),
        _isWaitingForResponse: isWaitingForResponseValue,
        get isWaitingForResponse() {
            return this._isWaitingForResponse;
        },
        set isWaitingForResponse(value) {
            this._isWaitingForResponse = value;
        }
    }

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [{provide: ChatService, useValue: chatServiceMock}],
        });

        chatboxComponent = new ChatboxComponent(chatServiceMock as any); 
        
        chatServiceMock.createConversation.calls.reset();
        chatServiceMock.setActiveConversation.calls.reset();
        chatServiceMock.deleteConversation.calls.reset();
        chatServiceMock.sendMessage.calls.reset();
        chatServiceMock.sendFeedback.calls.reset();
        chatServiceMock._isWaitingForResponse = false;
    });

    it('should create a chatbox', () => {
        expect(chatboxComponent).toBeTruthy();
    });

    it('should update messaes$', async() => {
        const messageMock: Message[] = [];
        for(let i = 0; i<3; ++i){
            messageMock.push({
                messageId: i.toString(),
                conversationId: '0',
                sender: 'user',
                content: 'test',
                createdAt: ''
            });
        }

        let conversationMock: Conversation;
        
        conversationMock = {
            conversationId: '0',
            sessionId: '12345',
            createdAt: '',
            updatedAt: '',
            toDelete: false,
        };

        (chatServiceMock.messages$ as BehaviorSubject<Message[]>).next(messageMock);
        chatboxComponent.ngOnInit();

        const mexObserver = await firstValueFrom(chatboxComponent.messages$);

        expect(mexObserver.length).toEqual(3);
    });

    it('should be no messages', async() => {
        const messageMock: Message[] = [];

        let conversationMock: Conversation;
        
        conversationMock = {
            conversationId: '0',
            sessionId: '12345',
            createdAt: '',
            updatedAt: '',
            toDelete: false,
        };

        (chatServiceMock.messages$ as BehaviorSubject<Message[]>).next(messageMock);
        chatboxComponent.ngOnInit();

        const mexObserver = await firstValueFrom(chatboxComponent.messages$);
        expect(mexObserver.length).toEqual(0);
    });

    it('should scroll to bottom', async() => {
        const messageMock: Message[] = [];
        for(let i = 0; i<3; ++i){
            messageMock.push({
                messageId: i.toString(),
                conversationId: '0',
                sender: 'user',
                content: 'test',
                createdAt: ''
            });
        }

        let conversationMock: Conversation;
        
        conversationMock = {
            conversationId: '0',
            sessionId: '12345',
            createdAt: '',
            updatedAt: '',
            toDelete: false,
        };

        (chatServiceMock.messages$ as BehaviorSubject<Message[]>).next(messageMock);
        chatboxComponent.ngOnInit();

        const scrollSpy = spyOn<any>(chatboxComponent, 'scrollToBottom');
        chatboxComponent.ngAfterViewChecked();  

        expect(scrollSpy).toHaveBeenCalled();
    });

    it('should send a message', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.messageText = 'test';
        chatServiceMock._isWaitingForResponse = false;
        
        chatboxComponent.sendMessage();

        expect(chatServiceMock.sendMessage).toHaveBeenCalled();
    });

    it('should not send a empty message', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.messageText = '';
        chatServiceMock._isWaitingForResponse = false;
        
        chatboxComponent.sendMessage();

        expect(chatServiceMock.sendMessage).not.toHaveBeenCalled();
    });

    it('should not send a message longer than the limit', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.messageText = 'a'.repeat(501);
        chatServiceMock._isWaitingForResponse = false;
        const alertSpy = spyOn(window, 'alert');
        
        chatboxComponent.sendMessage();

        expect(chatServiceMock.sendMessage).not.toHaveBeenCalled();
        expect(alertSpy).toHaveBeenCalledWith(`Il messaggio non può superare i ${chatboxComponent.MAX_MESSAGE_LENGTH} caratteri.`);
    });

    it('should not send a message while waiting', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.messageText = 'test';
        chatServiceMock._isWaitingForResponse = true;
        
        chatboxComponent.sendMessage();

        expect(chatServiceMock.sendMessage).not.toHaveBeenCalled();
    });

    it('should send a positive feedback', async() => {
        const feedbackMessageIdMock = '0';
        const feedbackIsPositiveMock = true;
        const feedbackContentMock = '';
        const showFeedbackPopupMock = true;

        chatboxComponent.ngOnInit(); 
        chatboxComponent.sendPositiveFeedback('0');
        
        expect(chatboxComponent.feedbackMessageId).toEqual(feedbackMessageIdMock);
        expect(chatboxComponent.feedbackIsPositive).toEqual(feedbackIsPositiveMock);
        expect(chatboxComponent.feedbackContent).toEqual(feedbackContentMock);
        expect(chatboxComponent.showFeedbackPopup).toEqual(showFeedbackPopupMock);
    });

    it('should send a negative feedback', async() => {
        const feedbackMessageIdMock = '0';
        const feedbackIsPositiveMock = false;
        const feedbackContentMock = '';
        const showFeedbackPopupMock = true;

        chatboxComponent.ngOnInit(); 
        chatboxComponent.sendNegativeFeedback('0');
        
        expect(chatboxComponent.feedbackMessageId).toEqual(feedbackMessageIdMock);
        expect(chatboxComponent.feedbackIsPositive).toEqual(feedbackIsPositiveMock);
        expect(chatboxComponent.feedbackContent).toEqual(feedbackContentMock);
        expect(chatboxComponent.showFeedbackPopup).toEqual(showFeedbackPopupMock);
    });

    it('should submit a feedback', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.feedbackMessageId = '0';
        
        chatboxComponent.submitFeedback();

        expect(chatServiceMock.sendFeedback).toHaveBeenCalled();
        expect(chatboxComponent.showFeedbackPopup).toEqual(false);
        expect(chatboxComponent.feedbackMessageId).toBeNull();
    });

    it('should not submit a feedback without feedbackMessageId', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.feedbackMessageId = null;
        
        chatboxComponent.submitFeedback();

        expect(chatServiceMock.sendFeedback).not.toHaveBeenCalled();
    });

    it('should call closeFeedbackPopup', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.showFeedbackPopup = true;
        chatboxComponent.feedbackMessageId = '0';

        chatboxComponent.closeFeedbackPopup();
        expect(chatboxComponent.showFeedbackPopup).toEqual(false);
        expect(chatboxComponent.feedbackMessageId).toBeNull();
    });

    it('should calculate remaining feedback chars', () => {
        chatboxComponent.feedbackContent = 'test';
        expect(chatboxComponent.remainingFeedbackChars).toEqual(chatboxComponent.MAX_FEEDBACK_LENGTH - chatboxComponent.feedbackContent.length);
    });
});
