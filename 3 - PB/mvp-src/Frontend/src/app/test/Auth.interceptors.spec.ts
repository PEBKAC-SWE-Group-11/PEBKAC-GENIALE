import { of, Observable, firstValueFrom } from "rxjs";
import { AuthInterceptor } from "../Core/Interceptors/Auth.interceptor";
import { HttpRequest, HttpResponse, HttpEvent } from "@angular/common/http";

describe('Auth.interceptors', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it('should test auth interceptors', () => {
        localStorage.setItem('adminToken', 'token');
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