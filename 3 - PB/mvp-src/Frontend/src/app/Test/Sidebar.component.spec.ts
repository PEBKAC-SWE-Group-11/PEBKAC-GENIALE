import { TestBed } from '@angular/core/testing';
import { ChatService } from '../Shared/Services/Chat.service';
import { BehaviorSubject, firstValueFrom } from 'rxjs';
import { Message } from '../Shared/Models/Message.model';
import { Conversation } from '../Shared/Models/Conversation.model';
import { SidebarComponent } from '../Core/Sidebar/Sidebar.component';

describe('Sidebar.component', () => {
    let sidebarComponent: SidebarComponent;
    
    const isWaitingForResponseValue = false;
    let chatServiceMock = { 
        conversations$: new BehaviorSubject<Conversation[]>([]),
        activeConversation$: new BehaviorSubject<Conversation | null>(null),
        messages$: new BehaviorSubject<Message[]>([]),
        createConversation: jasmine.createSpy('createConversation').and.returnValue(Promise.resolve()),
        setActiveConversation: jasmine.createSpy('setActiveConversation'),
        loadMessages: jasmine.createSpy('loadMessages'),
        updateConversationTimestamp: jasmine.createSpy('updateConversationTimestamp'),
        sendMessage: jasmine.createSpy('sendMessage'),
        updateConversationOrder: jasmine.createSpy('updateConversationOrder'),
        deleteConversation: jasmine.createSpy('deleteConversation'),
        sendFeedback: jasmine.createSpy('sendFeedback'),
        hasReachedConversationLimit: jasmine.createSpy('hasReachedConversationLimit').and.returnValue(false),
        _isWaitingForResponse: isWaitingForResponseValue,
        get isWaitingForResponse() {
            return this._isWaitingForResponse;
        },
        set isWaitingForResponse(value) {
            this._isWaitingForResponse = value;
        }
    };

    beforeEach(() =>{
        TestBed.configureTestingModule({
            providers: [{provide: ChatService, useValue: chatServiceMock}],
        });

        sidebarComponent = new SidebarComponent(chatServiceMock as any);
        
        chatServiceMock.createConversation.calls.reset();
        chatServiceMock.setActiveConversation.calls.reset();
        chatServiceMock.deleteConversation.calls.reset();
        chatServiceMock.hasReachedConversationLimit.calls.reset();
        chatServiceMock._isWaitingForResponse = false;
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
        chatServiceMock.hasReachedConversationLimit.and.returnValue(true);
        expect(sidebarComponent.hasReachedLimit).toBe(true);
    });


    it('should create a conversation', async() => {
        sidebarComponent.ngOnInit();
        chatServiceMock.hasReachedConversationLimit.and.returnValue(false);
        chatServiceMock.createConversation.and.returnValue(Promise.resolve());
        chatServiceMock._isWaitingForResponse = false;
        const emitSpy = spyOn(sidebarComponent.newConversationCreated, 'emit');
        
        sidebarComponent.createNewConversation();
        await Promise.resolve();
        
        expect(emitSpy).toHaveBeenCalled();
        expect(chatServiceMock.createConversation).toHaveBeenCalled();
    });

    it('should not create a conversation if it is waiting for a resposne', async() => {
        sidebarComponent.ngOnInit();
        chatServiceMock.hasReachedConversationLimit.and.returnValue(false);
        chatServiceMock.createConversation.and.returnValue(Promise.resolve());
        chatServiceMock._isWaitingForResponse = true;
        
        sidebarComponent.createNewConversation();
        await Promise.resolve();
        
        expect(chatServiceMock.createConversation).not.toHaveBeenCalled();
    });

    it('should have been reached conv limit', async() => {
        sidebarComponent.ngOnInit();
        chatServiceMock.hasReachedConversationLimit.and.returnValue(true);
        chatServiceMock._isWaitingForResponse = false;
        chatServiceMock.createConversation.and.returnValue(Promise.resolve());
        
        const confirmSpy = spyOn(window, 'confirm').and.returnValue(true);
        sidebarComponent.createNewConversation();
        await Promise.resolve();
        
        expect(confirmSpy).toHaveBeenCalledWith(
            `Hai raggiunto il limite massimo di ${sidebarComponent.MAX_CONVERSATIONS} conversazioni. ` +
            `Premendo OK verrà eliminata la conversazione più vecchia per fare spazio a quella nuova.`
        );
        expect(chatServiceMock.createConversation).toHaveBeenCalled();
    });

    it('should not be waiting for response', async() => {
        chatServiceMock._isWaitingForResponse = false;
        expect(sidebarComponent.isWaitingForResponse).toEqual(false);
    });

    it('should be waiting for a response', async() => {
        chatServiceMock._isWaitingForResponse = true;
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
        
        chatServiceMock._isWaitingForResponse = false;
        chatServiceMock.setActiveConversation.and.returnValue(conversationMock[0]);
        const conversationSelectedSpy = spyOn(sidebarComponent.conversationSelected, 'emit');
        
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
        
        chatServiceMock._isWaitingForResponse = true;
        const conversationSelectedSpy = spyOn(sidebarComponent.conversationSelected, 'emit');
        
        sidebarComponent.selectConversation(conversationMock[0]);
        
        expect(conversationSelectedSpy).not.toHaveBeenCalled();
    });

    it('should delete a conversation', async() => {
        sidebarComponent.ngOnInit();
        const mockEvent = { stopPropagation: jasmine.createSpy('stopPropagation') } as unknown as Event;
        chatServiceMock._isWaitingForResponse = false;
        
        sidebarComponent.deleteConversation(mockEvent, '0');
        
        expect(mockEvent.stopPropagation).toHaveBeenCalled();
        expect(chatServiceMock.deleteConversation).toHaveBeenCalled();
    });

    it('should not delete a conversation if it is waiting for a response', async() => {
        sidebarComponent.ngOnInit();
        const mockEvent = { stopPropagation: jasmine.createSpy('stopPropagation') } as unknown as Event;
        chatServiceMock._isWaitingForResponse = true;
        
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
        
        chatServiceMock._isWaitingForResponse = false;
        chatServiceMock.setActiveConversation.and.returnValue(conversationMock[0]);

        sidebarComponent.selectConversation(conversationMock[0]);
        
        expect(sidebarComponent.isActive(conversationMock[0])).toEqual(true);
        expect(sidebarComponent.isActive(conversationMock[1])).toEqual(false);
    })
});
