import { ChatboxComponent } from "../Core/Chatbox/Chatbox.component";
import { Message } from "../Shared/Models/Message.model";
import { Conversation } from "../Shared/Models/Conversation.model";
import { ChatService } from "../Shared/Services/Chat.service";
import { BehaviorSubject, Observable, firstValueFrom } from 'rxjs';
import { TestBed } from "@angular/core/testing";
import { of } from 'rxjs';

describe('chatbox.component', () => {
    let chatboxComponent: ChatboxComponent;

    let chatServiceMock = {
        conversations$: new BehaviorSubject<Conversation[]>([]),
        activeConversation$: new BehaviorSubject<Conversation | null>(null),
        messages$: new BehaviorSubject<Message[]>([]),
        createConversation: jest.fn(),
        setActiveConversation: jest.fn(),
        loadMessages: jest.fn(),
        updateConversationTimestamp: jest.fn(),
        sendMessage: jest.fn(),
        updateConversationOrder: jest.fn(),
        deleteConversation: jest.fn(),
        sendFeedback: jest.fn(),
        hasReachedConversationLimit: jest.fn(),
        get isWaitingForResponse(){
            return false;
        },
    }

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [{provide: ChatService, usaValue: chatServiceMock}],
        });

        chatboxComponent = new ChatboxComponent(chatServiceMock as any); 
        jest.clearAllMocks();
    });

    it('should create a chatbox', () => {
        expect(chatboxComponent).toBeTruthy();
    });

    //ngOnInit

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


    //ngAfterViewChecked

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

        const scrollSpy = jest.spyOn(chatboxComponent as any, 'scrollToBottom');
        chatboxComponent.ngAfterViewChecked();  

        expect(scrollSpy).toHaveBeenCalled();
    });

    
    //sendMessage

    it('should send a message', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.messageText = 'test';
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(false);
        chatServiceMock.sendMessage.mockResolvedValue(undefined);
        chatboxComponent.sendMessage();

        expect(chatServiceMock.sendMessage).toHaveBeenCalled();
    });

    it('should not send a empty message', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.messageText = '';
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(false);
        
        chatServiceMock.sendMessage.mockResolvedValue(undefined);
        chatboxComponent.sendMessage();

        expect(chatServiceMock.sendMessage).not.toHaveBeenCalled();
    });

    it('should not send a message longer than the limit', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.messageText = 'a'.repeat(501);
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(false);
        const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});
        
        chatServiceMock.sendMessage.mockResolvedValue(undefined);
        chatboxComponent.sendMessage();

        expect(chatServiceMock.sendMessage).not.toHaveBeenCalled();
        expect(alertSpy).toHaveBeenCalledWith(`Il messaggio non può superare i ${chatboxComponent.MAX_MESSAGE_LENGTH} caratteri.`)
    });

    it('should not send a message while waiting', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.messageText = 'test'
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(true);
        
        chatServiceMock.sendMessage.mockResolvedValue(undefined);
        chatboxComponent.sendMessage();

        expect(chatServiceMock.sendMessage).not.toHaveBeenCalled();
    });


    //sendPositiveFeedback

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


    //sendNegativeFeedback

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


    //submitFeedback

    it('should submit a feedback', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.feedbackMessageId = '0';
        chatServiceMock.sendFeedback.mockResolvedValue(undefined);
        chatboxComponent.submitFeedback();

        expect(chatServiceMock.sendFeedback).toHaveBeenCalled();
        expect(chatboxComponent.showFeedbackPopup).toEqual(false);
        expect(chatboxComponent.feedbackMessageId).toBeNull();
    });

    it('should not submit a feedback without feedbackMessageId', async() => {
        chatboxComponent.ngOnInit();
        chatServiceMock.sendFeedback.mockResolvedValue(undefined);
        chatboxComponent.submitFeedback();

        expect(chatServiceMock.sendFeedback).not.toHaveBeenCalled();
    });


    //closeFeedbackPopup

    it('should call closeFeedbackPopup', async() => {
        chatboxComponent.ngOnInit();
        chatboxComponent.showFeedbackPopup = true;
        chatboxComponent.feedbackMessageId = '0';

        chatboxComponent.closeFeedbackPopup();
        expect(chatboxComponent.showFeedbackPopup).toEqual(false);
        expect(chatboxComponent.feedbackMessageId).toBeNull();
    });


    //remainingFeedbackChars

    it('should calculate remaining feedback chars', () => {
        chatboxComponent.feedbackContent = 'test';
        expect(chatboxComponent.remainingFeedbackChars).toEqual(chatboxComponent.MAX_FEEDBACK_LENGTH - chatboxComponent.feedbackContent.length);
    });
})