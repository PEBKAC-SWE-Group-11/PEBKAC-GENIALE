import { of, Observable, firstValueFrom } from "rxjs";
import { HttpTestingController } from "@angular/common/http/testing";
import { HttpClientTestingModule } from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";
import { AuthInterceptor } from "../core/interceptors/auth.interceptor";
import { HttpRequest, HttpHandlerFn, HttpInterceptorFn, HttpResponse, HttpEvent } from "@angular/common/http";

describe('auth.interceptors', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it('should test auth interceptors', () => {
        localStorage.setItem('admin_token', 'token');
        const req = new HttpRequest('GET', 'https://api.example.com/admin/stats');
        const mockResponse = new HttpResponse({ status: 200, body: 'Success' });

        const nextMock = jest.fn((req: HttpRequest<unknown>): Observable<HttpEvent<unknown>> => {
            return of();
        });

        
        const result = AuthInterceptor(req, nextMock);

        const modifiedRequest = nextMock.mock.calls[0][0] as HttpRequest<unknown>;

        expect(modifiedRequest.headers.get('Authorization')).toBe('Bearer token');
    });

    it('should return next', async() => {
        const req = new HttpRequest('GET', 'https://api.example.com/admin/stats');
        const mockResponse = new HttpResponse({ status: 200, body: 'Success' });

        const nextMock = jest.fn((req: HttpRequest<unknown>): Observable<HttpEvent<unknown>> => {
            return of(mockResponse);
        });
        
        const result = await firstValueFrom(AuthInterceptor(req, nextMock));
        expect(nextMock).toHaveBeenCalledWith(req);  
        expect(result).toEqual(mockResponse);
    });

});