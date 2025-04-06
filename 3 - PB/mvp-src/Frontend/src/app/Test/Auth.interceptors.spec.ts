import { of, Observable, firstValueFrom } from "rxjs";
import { AuthInterceptor } from "../Core/Interceptors/Auth.interceptor";
import { HttpRequest, HttpResponse, HttpEvent } from "@angular/common/http";

describe('Auth.interceptors', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it('should test auth interceptors', async() => {
        localStorage.setItem('adminToken', 'token');
        const req = new HttpRequest('GET', 'https://api.example.com/admin/stats');
        const mockResponse = new HttpResponse({ status: 200, body: 'Success' });

        // Creiamo il mock usando jasmine direttamente per evitare problemi con Observable
        const nextMock = jasmine.createSpy('nextFn').and.returnValue(of(mockResponse));

        const result = await firstValueFrom(AuthInterceptor(req, nextMock));

        const modifiedRequest = nextMock.calls.argsFor(0)[0] as HttpRequest<unknown>;

        expect(modifiedRequest.headers.get('Authorization')).toBe('Bearer token');
        expect(nextMock).toHaveBeenCalledWith(jasmine.any(Object)); 
        expect(result).toEqual(mockResponse);
    });

    it('should return next', async() => {
        const req = new HttpRequest('GET', 'https://api.example.com/admin/stats');
        const mockResponse = new HttpResponse({ status: 200, body: 'Success' });

        // Creiamo il mock usando jasmine direttamente per evitare problemi con Observable
        const nextMock = jasmine.createSpy('nextFn').and.returnValue(of(mockResponse));
        
        const result = await firstValueFrom(AuthInterceptor(req, nextMock));
        expect(nextMock).toHaveBeenCalledWith(req);  
        expect(result).toEqual(mockResponse);
    });

});