import { AdminLoginComponent } from "../features/admin/login/login.component";
import { TestBed } from "@angular/core/testing";
import { ApiService } from "../shared/services/api.service";
import { Router } from "@angular/router";
import { of } from "rxjs";

describe('dashboard.component', () => {
    let loginComponent: AdminLoginComponent;
    
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
        adminLogin: jest.fn(),
    };

    let routerMock = {
        navigate: jest.fn(),
    }

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: ApiService, useValue: apiServiceMock },
                { provide: Router, useValue: routerMock }
            ]
        });

        loginComponent = new AdminLoginComponent(apiServiceMock as any, routerMock as any);

        const mockDigest = jest.fn().mockImplementation(() => {
            const buffer = new ArrayBuffer(32);
            const view = new Uint8Array(buffer);
            for (let i = 0; i < 32; i++) {
                view[i] = i + 1;
            }
            return Promise.resolve(buffer);
        });
    
        Object.defineProperty(globalThis, 'crypto', {
            value: {
                subtle: {
                    digest: mockDigest,
                },
            },
            configurable: true,
        });

        loginComponent.password = '';
        localStorage.clear();
        jest.clearAllMocks();
    });

    it('should build an instance', async() => {
        expect(loginComponent).toBeTruthy();
    });

    it('should hash the password', async() => {
        const mockDigest = jest.fn().mockImplementation(() => {
            const buffer = new ArrayBuffer(32);
            const view = new Uint8Array(buffer);
            for (let i = 0; i < 32; i++) {
                view[i] = i + 1;
            }
            return Promise.resolve(buffer);
        });
    
        Object.defineProperty(globalThis, 'crypto', {
            value: {
                subtle: {
                    digest: mockDigest,
                },
            },
            configurable: true,
        });

        const hashedPassword = await loginComponent.hashPassword('password');
        await Promise.resolve();
        
        expect(hashedPassword.length).toEqual(64);
        expect(mockDigest).toHaveBeenCalled();
    });

    it('should log in', async() => {
        const adminLoginMock = { success: true };
        loginComponent.password = 'password';
        apiServiceMock.adminLogin.mockReturnValue(of(adminLoginMock));
        
        await loginComponent.login();

        expect(localStorage.getItem('adminAuthenticated')).toEqual('true');
        expect(loginComponent.errorMessage).toEqual('');
    });

    it('should not log in without a password', async() => {
        const adminLoginMock = { success: true };
        loginComponent.password = '';
        apiServiceMock.adminLogin.mockReturnValue(of(adminLoginMock));

        await loginComponent.login();

        expect(loginComponent.errorMessage).toEqual('Inserisci la password');
        expect(apiServiceMock.adminLogin).not.toHaveBeenCalled();
    });

    it('should not log in without success resposne', async() => {
        const adminLoginMock = { success: false };
        loginComponent.password = 'password';
        apiServiceMock.adminLogin.mockReturnValue(of(adminLoginMock));

        await loginComponent.login();

        expect(loginComponent.errorMessage).toEqual('Password non valida');
    });

    it('should authenticate the token', async() => {
        const adminLoginMock = { success: true, token: 'token' };
        loginComponent.password = 'password';
        apiServiceMock.adminLogin.mockReturnValue(of(adminLoginMock));

        await loginComponent.login();

        expect(loginComponent.errorMessage).toEqual('');
        expect(localStorage.getItem('adminToken')).toEqual('token');
    });
});