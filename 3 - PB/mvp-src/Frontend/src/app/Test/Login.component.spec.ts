import { AdminLoginComponent } from "../Features/Admin/Login/Login.component";
import { TestBed } from "@angular/core/testing";
import { ApiService } from "../Shared/Services/Api.service";
import { Router } from "@angular/router";
import { of } from "rxjs";

describe('Dashboard.component', () => {
    let loginComponent: AdminLoginComponent;
    
    let apiServiceMock = {
        createSession: jasmine.createSpy('createSession'),
        deleteConversation: jasmine.createSpy('deleteConversation'),
        createConversation: jasmine.createSpy('createConversation'),
        getMessages: jasmine.createSpy('getMessages'),
        updateSession: jasmine.createSpy('updateSession'),
        getConversations: jasmine.createSpy('getConversations'),
        sendMessage: jasmine.createSpy('sendMessage'),
        updateConversationTimestamp: jasmine.createSpy('updateConversationTimestamp'),
        sendFeedback: jasmine.createSpy('sendFeedback'),
        askQuestion: jasmine.createSpy('askQuestion'),
        readSession: jasmine.createSpy('readSession'),
        getAdminStats: jasmine.createSpy('getAdminStats'),
        getFeedbackWithComments: jasmine.createSpy('getFeedbackWithComments'),
        adminLogin: jasmine.createSpy('adminLogin'),
    };

    let routerMock = {
        navigate: jasmine.createSpy('navigate')
    }

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: ApiService, useValue: apiServiceMock },
                { provide: Router, useValue: routerMock }
            ]
        });

        loginComponent = new AdminLoginComponent(apiServiceMock as any, routerMock as any);

        const mockDigest = jasmine.createSpy('digest').and.callFake(() => {
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
        
        apiServiceMock.adminLogin.calls.reset();
        routerMock.navigate.calls.reset();
    });

    it('should build an instance', async() => {
        expect(loginComponent).toBeTruthy();
    });

    it('should hash the password', async() => {
        // Mock per crypto.subtle.digest
        const mockDigest = jasmine.createSpy('digest').and.callFake(() => {
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
        apiServiceMock.adminLogin.and.returnValue(of(adminLoginMock));
        
        await loginComponent.login();

        expect(localStorage.getItem('adminAuthenticated')).toEqual('true');
        expect(loginComponent.errorMessage).toEqual('');
    });

    it('should not log in without a password', async() => {
        const adminLoginMock = { success: true };
        loginComponent.password = '';
        apiServiceMock.adminLogin.and.returnValue(of(adminLoginMock));

        await loginComponent.login();

        expect(loginComponent.errorMessage).toEqual('Inserisci la password');
        expect(apiServiceMock.adminLogin).not.toHaveBeenCalled();
    });

    it('should not log in without success response', async() => {
        const adminLoginMock = { success: false };
        loginComponent.password = 'password';
        apiServiceMock.adminLogin.and.returnValue(of(adminLoginMock));

        await loginComponent.login();

        expect(loginComponent.errorMessage).toEqual('Password non valida');
    });

    it('should authenticate the token', async() => {
        const adminLoginMock = { success: true, token: 'token' };
        loginComponent.password = 'password';
        apiServiceMock.adminLogin.and.returnValue(of(adminLoginMock));

        await loginComponent.login();

        expect(loginComponent.errorMessage).toEqual('');
        expect(localStorage.getItem('adminToken')).toEqual('token');
    });
});
