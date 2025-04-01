import { ChatboxComponent } from "../core/chatbox/chatbox.component";
import { Message } from "../shared/models/message.model";
import { Conversation } from "../shared/models/conversation.model";
import { ChatService } from "../shared/services/chat.service";
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

        const scrollSpy = jest.spyOn(chatboxComponent as any, 'scrollToBottom');
        chatboxComponent.ngAfterViewChecked();  

        expect(scrollSpy).toHaveBeenCalled();
    });
})