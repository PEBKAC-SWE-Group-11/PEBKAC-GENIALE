import { ApiService } from '../Shared/Services/Api.service';
import { TestBed } from "@angular/core/testing";
import { HttpClientTestingModule, HttpTestingController } from "@angular/common/http/testing";
import { Conversation } from '../Shared/Models/Conversation.model';
import { Message } from '../Shared/Models/Message.model';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../Environment/Environment';

describe('Api.service', () => {   
    let service: ApiService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [ApiService]
        });

        service = TestBed.inject(ApiService);
        httpMock = TestBed.inject(HttpTestingController);
    });
    
    afterEach(() => {
        // Verificare che non ci siano richieste HTTP in sospeso
        httpMock.verify();
    });

    it('should create a session', async() => {
        let apiUrl = environment.apiUrl;
        let sessionMock = { sessionId: '12345' }

        let response = firstValueFrom(service.createSession());

        const req = httpMock.expectOne(`${apiUrl}/api/session`);
        expect(req.request.method).toBe('POST');

        req.flush(sessionMock);
        const promise = await response;

        expect(promise).toEqual(sessionMock);
    });


    it('should update the session', async() => {
        let apiUrl = environment.apiUrl;
        let updateSessionId = '54321';
        const updateResponseMock = { success: true };

        const updateResponse = firstValueFrom(service.updateSession('54321'));

        const req2 = httpMock.expectOne(`${apiUrl}/api/session/${updateSessionId}`);
        expect(req2.request.method).toBe('PUT');

        req2.flush(updateResponseMock);
        const promise2 = await updateResponse;

        expect(promise2).toBe(updateResponseMock);
    });


    it('should create a conversation', async() => {
        const apiUrl = environment.apiUrl;
        const sessionId = '12345';

        const promise = firstValueFrom(service.createConversation(sessionId));

        const req = httpMock.expectOne(`${apiUrl}/api/conversation`);
        expect(req.request.method).toBe('POST');

        req.flush({ conversationId: '1' });
        const response = await promise;

        expect(response).toEqual({ conversationId: '1'});
    });

    it('should get the conversations', async() => {
        const apiUrl = environment.apiUrl;
        const sessionId = '12345';

        const conversationsMock: Conversation[] = [];

        conversationsMock.push({
            conversationId: '1',
            sessionId: sessionId,
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test'
        });

        conversationsMock.push({
            conversationId: '2',
            sessionId: sessionId,
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test2'
        });

        conversationsMock.push({
            conversationId: '3',
            sessionId: sessionId,
            createdAt: '',
            updatedAt: '',
            toDelete: false,
            title: 'test3'
        });

        const response = firstValueFrom(service.getConversations(sessionId));

        const req = httpMock.expectOne(`${apiUrl}/api/conversation?sessionId=${sessionId}`);
        expect(req.request.method).toBe('GET');

        req.flush(conversationsMock);
        const promise = await response;
        
        expect(promise).toEqual(conversationsMock);
    });

    it('should delete a conversation by id', async() => {
        const apiUrl = environment.apiUrl;

        const response = firstValueFrom(service.deleteConversation('1'));

        const req = httpMock.expectOne(`${apiUrl}/api/conversation/1`);
        expect(req.request.method).toBe('DELETE');

        req.flush(null);
        const promise = await response;
        
        expect(promise).toBeNull();
    });

    it('should send a message', async() => {
        const apiUrl = environment.apiUrl;
        const sessionId = '12345';
        const conversationId = '1';
        const messageIdMock = { messageId: '1' };
        const messageMock = {
            messageId: '1',
            conversationId: '1',
            sender: 'user',
            content: 'ciao',
            createdAt: ''
        }

        const response = firstValueFrom(service.sendMessage('1', 'ciao'));

        const req = httpMock.expectOne(`${apiUrl}/api/message`);
        expect(req.request.method).toBe('POST');

        req.flush(messageIdMock);
        const promise = await response;

        expect(promise).toEqual(messageIdMock);
    });

    it('should get the messages', async() => {
        const apiUrl = environment.apiUrl;
        const sessionId = '12345';
        const conversationId = '1';
        let messagesMock: Message[] = [];

        messagesMock.push({
            messageId: '1',
            conversationId: conversationId,
            sender: 'user',
            content: 'ciao',
            createdAt: ''
        });

        messagesMock.push({
            messageId: '2',
            conversationId: conversationId,
            sender: 'assistant',
            content: 'ciao',
            createdAt: ''
        });

        messagesMock.push({
            messageId: '3',
            conversationId: conversationId,
            sender: 'system',
            content: 'ciao',
            createdAt: ''
        });

        const response = firstValueFrom(service.getMessages('1'));

        const req = httpMock.expectOne(`${apiUrl}/api/message?conversationId=${conversationId}`);
        expect(req.request.method).toEqual('GET');

        req.flush(messagesMock);
        const promise = await response;

        expect(promise).toEqual(messagesMock);
    });

    it('should send feedback', async() => {
        const apiUrl = environment.apiUrl;
        const sessionId = '12345';
        const messageId = '1';
        const isPositive = true;
        const content = 'content';
        const feedbackMock = { messageId: '1' };

        const response = firstValueFrom(service.sendFeedback(messageId, isPositive, content));

        const req = httpMock.expectOne(`${apiUrl}/api/feedback`);
        expect(req.request.method).toBe('POST');

        req.flush(feedbackMock);

        const promise = await response;
        expect(promise).toEqual(feedbackMock);
    });

    it('should get feedback`s comment', async() => {
        const apiUrl = environment.apiUrl;
        const sessionId = '12345';
        const feedbackMock: any[] = [{
            feedback_id: '1',
            messageId: '1',
            type: 'positive',
            content: 'content',
            createdAt: ''
        }];

        const response = firstValueFrom(service.getFeedbackWithComments());

        const req = httpMock.expectOne(`${apiUrl}/api/dashboard/feedbackComments`);
        expect(req.request.method).toBe('GET');

        req.flush(feedbackMock);

        const promise = await response;
        expect(promise).toEqual(feedbackMock);
    });

    it('should test if the password is correct', async() => {
        // Nota: adminLogin usa un mock interno, quindi non dobbiamo usare HttpTestingController
        const passwordMock = '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'; // Hash di "password"
        const response = firstValueFrom(service.adminLogin(passwordMock));
        const result = await response;
        
        expect(result.success).toBe(true);
        expect(result.token).toBeTruthy();
    });

    it('should test if the password is not correct', async() => {
        // Nota: adminLogin usa un mock interno, quindi non dobbiamo usare HttpTestingController
        const passwordMock = 'password_sbagliata';
        const response = firstValueFrom(service.adminLogin(passwordMock));
        const result = await response;
        
        expect(result.success).toBe(false);
        expect(result.token).toBeFalsy();
    });

    it('should get admin stats', async() => {
        const apiUrl = environment.apiUrl;

        const getConvMock = { numConversations: 3 };
        const getPosMock = { numPositiveFeedback: 2 };
        const getNegMock = { numNegativeFeedback: 1 };

        const statsMock = {
            negativeFeedback: 1,
            positiveFeedback: 2,
            totalConversations: 3,
            totalMessages: 0,
            uniqueUsers: 0
        }

        const response = firstValueFrom(service.getAdminStats());

        const conversationRequest = httpMock.expectOne(`${apiUrl}/api/dashboard/numConversations`);
        const positiveFeedbacksRequest = httpMock.expectOne(`${apiUrl}/api/dashboard/numPositive`);
        const negativeFeedbacksRequest = httpMock.expectOne(`${apiUrl}/api/dashboard/numNegative`);

        conversationRequest.flush(getConvMock);
        positiveFeedbacksRequest.flush(getPosMock);
        negativeFeedbacksRequest.flush(getNegMock);

        const promise = await response;

        expect(promise).toEqual(statsMock);
    });

    it('should ask a question', async() => {
        const apiUrl = environment.apiUrl;
        const questionMock = { messageId: '1' };
        const conversationId = '1';
        
        const response = firstValueFrom(service.askQuestion(conversationId, 'test'));

        const req = httpMock.expectOne(`${apiUrl}/api/question/${conversationId}`);
        expect(req.request.method).toBe('POST')
        req.flush(questionMock);

        const promise = await response;
        expect(promise).toEqual(questionMock);
    });

    it('should read the session', async() => {
        const apiUrl = environment.apiUrl;
        const sessionIdMock = '12345'
        const sessionMock = { sessionId: sessionIdMock, isActive: true };
        
        const response = firstValueFrom(service.readSession(sessionIdMock));

        const req = httpMock.expectOne(`${apiUrl}/api/session/${sessionIdMock}`);
        expect(req.request.method).toBe('GET');

        req.flush(sessionMock);
        const promise = await response;
        expect(promise).toEqual(sessionMock);
    });
});