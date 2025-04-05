import { Router } from '@angular/router';
import { TestBed } from '@angular/core/testing';
import { AdminGuard } from '../Core/Guards/Admin.guard';

describe('Admin.guards', () => {
    let routerMock = {
        navigate: jest.fn(),
    }

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [{ provide: Router, useValue: routerMock }]
        });

        localStorage.clear();
    });

    it('should check if there is a token and if it is authenticated', async() => {
        localStorage.setItem("adminToken", 'token');
        localStorage.setItem("adminAuthenticated", 'true');

        const route = {} as any;
        const state = {} as any;

        const result = TestBed.runInInjectionContext(() => AdminGuard(route, state));

        expect(result).toEqual(true);
    });

    it('should return false without token', () => {
        const route = {} as any;
        const state = {} as any;

        const result = TestBed.runInInjectionContext(() => AdminGuard(route, state));

        expect(result).toEqual(false);
    });
});