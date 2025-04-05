import { ApiService } from "../Shared/Services/Api.service";
import { Router } from '@angular/router';
import { AdminDashboardComponent } from "../Features/Admin/Dashboard/Dashboard.component";
import { TestBed } from "@angular/core/testing";
import { of } from "rxjs";

describe('Dashboard.component', () => {
    let dashboard: AdminDashboardComponent;
    
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
        getAdminStats: jest.fn(),
        getFeedbackWithComments: jest.fn(),
    };

    let routerMock = {
        navigate: jest.fn(),
    };

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: ApiService, useValue: apiServiceMock },
                { provide: Router, useValue: routerMock }
            ]
        });

        dashboard = new AdminDashboardComponent(apiServiceMock as any, routerMock as any);
    });

    it('should build an instance', async() => {
        expect(dashboard).toBeTruthy();
    });

    it('should load stats and feedback comments', async() => {
        const adminStatsMock = {
            totalConversations: 1,
            positiveFeedback: 2,
            negativeFeedback: 3
        };

        const feedbackMock: any[] = [{
            feedback_id: '1',
            messageId: '1',
            type: 'positive',
            content: 'content',
            createdAt: ''
        }];

        apiServiceMock.getAdminStats.mockReturnValue(of(adminStatsMock));
        apiServiceMock.getFeedbackWithComments.mockReturnValue(of(feedbackMock));
        await dashboard.ngOnInit();
        await Promise.resolve();

        expect(dashboard.stats).toEqual(adminStatsMock);
        expect(dashboard.isLoading).toEqual(false);
        expect(dashboard.isLoadingComments).toEqual(false);
    });

    it('should calculate satisfaction rate', async() => {
        const adminStatsMock = {
            totalConversations: 1,
            positiveFeedback: 2,
            negativeFeedback: 3
        };

        const feedbackMock: any[] = [{
            feedback_id: '1',
            messageId: '1',
            type: 'positive',
            content: 'content',
            createdAt: ''
        }];

        apiServiceMock.getAdminStats.mockReturnValue(of(adminStatsMock));
        apiServiceMock.getFeedbackWithComments.mockReturnValue(of(feedbackMock));
        await dashboard.ngOnInit();
        await Promise.resolve();

        const result = dashboard.calcSatisfactionRate();

        expect(result).toEqual("40%");
    });

    it('satisfaction rate should be 0%', async() => {
        const adminStatsMock = {
            totalConversations: 1,
            positiveFeedback: 0,
            negativeFeedback: 0
        };

        const feedbackMock: any[] = [{
            feedback_id: '1',
            messageId: '1',
            type: 'positive',
            content: 'content',
            createdAt: ''
        }];

        apiServiceMock.getAdminStats.mockReturnValue(of(adminStatsMock));
        apiServiceMock.getFeedbackWithComments.mockReturnValue(of(feedbackMock));
        await dashboard.ngOnInit();
        await Promise.resolve();

        const result = dashboard.calcSatisfactionRate();

        expect(result).toEqual("0%");
    });


    it('should be no stats', async() => {
        const adminStatsMock = {};

        const feedbackMock: any[] = [{
            feedback_id: '1',
            messageId: '1',
            type: 'positive',
            content: 'content',
            createdAt: ''
        }];

        apiServiceMock.getAdminStats.mockReturnValue(of(adminStatsMock));
        apiServiceMock.getFeedbackWithComments.mockReturnValue(of(feedbackMock));
        await dashboard.ngOnInit();
        await Promise.resolve();

        const result = dashboard.calcSatisfactionRate();

        expect(result).toEqual("0%");
    });

    it('should format the date', async() => {
        const date = new Date();
        const formattedDate = dashboard.formatDate(date.toString());

        expect(formattedDate).toEqual(date.toLocaleString('it-IT'));
    });
});
