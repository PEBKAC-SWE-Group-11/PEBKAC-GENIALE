import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { CanActivateFn } from '@angular/router';
import { TestBed } from '@angular/core/testing';
import { AdminGuard } from '../Core/Guards/Admin.guard';

describe('admin.guards', () => {
    let routerMock = {
        navigate: jest.fn(),
    }

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [{ provide: Router, useValue: routerMock }]
        });

        localStorage.clear();
    });

    it('should check if token there is token and if it is authenticated', async() => {
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