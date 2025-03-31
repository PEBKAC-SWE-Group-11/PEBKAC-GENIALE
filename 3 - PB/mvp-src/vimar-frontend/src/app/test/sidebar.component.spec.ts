import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ChatService } from '../shared/services/chat.service';
import { ApiService } from '../shared/services/api.service';
import { BehaviorSubject, Observable, firstValueFrom } from 'rxjs';
import { Message } from '../shared/models/message.model';
import { Conversation } from '../shared/models/conversation.model';
import { environment } from '../../environments/environment';
import { SidebarComponent } from '../core/sidebar/sidebar.component';
import { of } from 'rxjs';

describe('sidebar.component', () => {
    let sidebarComponent: SidebarComponent;

    let chatServiceMock = { 
        conversations$: jest.fn(),
        activeConversation$: jest.fn(),
        messages$: jest.fn(),
        createConversation: jest.fn(),
        setActiveConversation: jest.fn(),
        loadMessages: jest.fn(),
        updateConversationTimestamp: jest.fn(),
        sendMessage: jest.fn(),
        updateConversationOrder: jest.fn(),
        deleteConversation: jest.fn(),
        sendFeedback: jest.fn(),
        hasReachedConversationLimit: jest.fn(),
        isWaitingForResponse: jest.fn(),
    };

    let httpMock: HttpTestingController;

    beforeEach(() =>{
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [{provide: ChatService, useValue: chatServiceMock}],
        });

        httpMock = TestBed.inject(HttpTestingController);
        sidebarComponent = new SidebarComponent(chatServiceMock as unknown as ChatService);
    });

    it('there should be an instance of sidebar', async() => {
        expect(sidebarComponent).toBeTruthy();
    });

    it('should test ngOnInit', async() => {
        const conversationMock: Conversation[] = [];
        for(let i = 0; i<3; ++i){
            conversationMock.push({
                conversationId: i.toString(),
                sessionId: '12345',
                createdAt: '',
                updatedAt: '',
                toDelete: false,
            });
        }

        chatServiceMock.conversations$.mockReturnValue(of(conversationMock));
        chatServiceMock.activeConversation$.mockReturnValue(of(conversationMock[0]));
        sidebarComponent.ngOnInit();

        const convObserver = await firstValueFrom(sidebarComponent.conversations$);

        expect(convObserver.length).toEqual(3);
    });

    /*it('should test ngOnDestroy', async() => {
        //??
    })

    it('should have reached the limit', async() => {
        chatServiceMock.hasReachedConversationLimit.mockReturnValue(true);
        expect(sidebarComponent.hasReachedLimit).toBe(true);
    });

    it('should be waiting for a response', async() => {
        chatServiceMock.isWaitingForResponse.mockReturnValue(of(true));
        sidebarComponent.ngOnInit();
        expect(sidebarComponent.isWaitingForResponse).toBe(true);
    });

    it('should create a conversation', async() => {

    })*/


});