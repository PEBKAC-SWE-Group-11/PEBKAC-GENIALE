import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ChatService } from '../Shared/Services/Chat.service';
import { BehaviorSubject, Observable, firstValueFrom } from 'rxjs';
import { Message } from '../Shared/Models/Message.model';
import { Conversation } from '../Shared/Models/Conversation.model';
import { SidebarComponent } from '../Core/Sidebar/Sidebar.component';

describe('sidebar.component', () => {
    let sidebarComponent: SidebarComponent;

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
    };

    beforeEach(() =>{
        TestBed.configureTestingModule({
            providers: [{provide: ChatService, useValue: chatServiceMock}],
        });

        sidebarComponent = new SidebarComponent(chatServiceMock as any);

        jest.clearAllMocks();
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
        (chatServiceMock.conversations$ as BehaviorSubject<Conversation[]>).next(conversationMock);
        sidebarComponent.ngOnInit();
        const convObserver = await firstValueFrom(sidebarComponent.conversations$);
        expect(convObserver.length).toEqual(3);
    });


    it('should have reached the limit', async() => {
        chatServiceMock.hasReachedConversationLimit.mockReturnValue(true);
        expect(sidebarComponent.hasReachedLimit).toBe(true);
    });


    it('should create a conversation', async() => {
        sidebarComponent.ngOnInit();
        chatServiceMock.hasReachedConversationLimit.mockReturnValue(false);
        chatServiceMock.createConversation.mockResolvedValue(undefined);
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(false);
        const emitSpy = jest.spyOn(sidebarComponent.newConversationCreated, 'emit');
        sidebarComponent.createNewConversation();
        await Promise.resolve();
        expect(emitSpy).toHaveBeenCalled();
        expect(chatServiceMock.createConversation).toHaveBeenCalled();
    });

    it('should should not create a conversation if it is waiting for a resposne', async() => {
        sidebarComponent.ngOnInit();
        chatServiceMock.hasReachedConversationLimit.mockReturnValue(false);
        chatServiceMock.createConversation.mockResolvedValue(undefined);
        const conv = sidebarComponent.createNewConversation();
        await Promise.resolve();
        expect(conv).toBeUndefined();
    });

    it('should have been reached conv limit', async() => {
        sidebarComponent.ngOnInit();
        chatServiceMock.hasReachedConversationLimit.mockReturnValue(true);
        chatServiceMock.createConversation.mockResolvedValue(undefined);
        const emitSpy = jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(false);
        const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
        const conv = sidebarComponent.createNewConversation();
        await Promise.resolve();
        expect(confirmSpy).toHaveBeenCalledWith(
            `Hai raggiunto il limite massimo di ${sidebarComponent.MAX_CONVERSATIONS} conversazioni. ` +
            `Premendo OK verrà eliminata la conversazione più vecchia per fare spazio a quella nuova.`
        );
        expect(emitSpy).toHaveBeenCalled();
        expect(chatServiceMock.createConversation).toHaveBeenCalled();
        confirmSpy.mockRestore();
    });

    it('should not be waiting for response', async() => {
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(false);
        expect(sidebarComponent.isWaitingForResponse).toEqual(false);
    });

    it('should be waiting for a response', async() => {
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(true);
        expect(sidebarComponent.isWaitingForResponse).toEqual(true);
    });

    it('should select a conversation', async() => {
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
        (chatServiceMock.conversations$ as BehaviorSubject<Conversation[]>).next(conversationMock);
        sidebarComponent.ngOnInit();
        
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(false);
        chatServiceMock.setActiveConversation.mockReturnValue(conversationMock[0]);
        const conversationSelectedSpy = jest.spyOn(sidebarComponent.conversationSelected, 'emit');
        
        sidebarComponent.selectConversation(conversationMock[0]);
        
        expect(conversationSelectedSpy).toHaveBeenCalled();
    });

    it('should not select a conversation if it is waiting for a response', async() => {
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
        (chatServiceMock.conversations$ as BehaviorSubject<Conversation[]>).next(conversationMock);
        sidebarComponent.ngOnInit();
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(true);
        const conversationSelectedSpy = jest.spyOn(sidebarComponent.conversationSelected, 'emit');
        
        sidebarComponent.selectConversation(conversationMock[0]);
        
        expect(conversationSelectedSpy).not.toHaveBeenCalled();
    });

    it('should delete a conversation', async() => {
        sidebarComponent.ngOnInit();
        const mockEvent = { stopPropagation: jest.fn() } as unknown as Event;
        const waitSpy = jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(false);
        chatServiceMock.deleteConversation.mockResolvedValue(undefined);

        sidebarComponent.deleteConversation(mockEvent, '0');
        
        expect(mockEvent.stopPropagation).toHaveBeenCalled();
        expect(chatServiceMock.deleteConversation).toHaveBeenCalled();
    });

    it('should not delete a conversation if it is waiting for a response', async() => {
        sidebarComponent.ngOnInit();
        const mockEvent = { stopPropagation: jest.fn() } as unknown as Event;
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(true);
        expect(sidebarComponent.isWaitingForResponse).toBe(true);
        chatServiceMock.deleteConversation.mockResolvedValue(undefined);

        sidebarComponent.deleteConversation(mockEvent, '0');
        
        expect(mockEvent.stopPropagation).toHaveBeenCalled();
        expect(chatServiceMock.deleteConversation).not.toHaveBeenCalled();
    });

    it('should set the activeConversation variable', async() => {
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
        (chatServiceMock.conversations$ as BehaviorSubject<Conversation[]>).next(conversationMock);
        (chatServiceMock.activeConversation$ as BehaviorSubject<Conversation>).next(conversationMock[0]);
        sidebarComponent.ngOnInit();
        
        jest.spyOn(chatServiceMock, 'isWaitingForResponse', 'get').mockReturnValue(false);
        chatServiceMock.setActiveConversation.mockReturnValue(conversationMock[0]);
        const conversationSelectedSpy = jest.spyOn(sidebarComponent.conversationSelected, 'emit');

        sidebarComponent.selectConversation(conversationMock[0]);
        
        expect(sidebarComponent.isActive(conversationMock[0])).toEqual(true);
        expect(sidebarComponent.isActive(conversationMock[1])).toEqual(false);
    })
});