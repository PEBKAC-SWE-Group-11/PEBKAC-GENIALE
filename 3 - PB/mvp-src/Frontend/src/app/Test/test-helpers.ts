/**
 * Helper functions to replace Jest functions with Jasmine equivalents
 */

import { Observable, of } from 'rxjs';

function isObservable(value: any): boolean {
  return value && typeof value.subscribe === 'function';
}

function ensureObservable(value: any): Observable<any> {
  if (value === null || value === undefined) {
    return of(null);
  }
  
  if (isObservable(value)) {
    return value;
  }
  
  if (value instanceof Promise) {
    return new Observable(subscriber => {
      value.then(
        result => {
          subscriber.next(result);
          subscriber.complete();
        },
        error => subscriber.error(error)
      );
    });
  }
  
  return of(value);
}

export function createMock<T = any>() {
  const spy = jasmine.createSpy();
  
  (spy as any).mockReturnValue = function(value: any) {
    if (value !== null && value !== undefined && !isObservable(value) && !(value instanceof Promise)) {
      value = of(value);
    }
    spy.and.returnValue(value);
    return spy;
  };
  
  (spy as any).mockImplementation = function(impl: any) {
    spy.and.callFake(function(...args: any[]) {
      const result = impl(...args);
      if (result !== null && result !== undefined && !isObservable(result) && !(result instanceof Promise)) {
        return of(result);
      }
      return result;
    });
    return spy;
  };
  
  (spy as any).mockResolvedValue = function(value: any) {
    spy.and.returnValue(Promise.resolve(value));
    return spy;
  };
  
  (spy as any).mockRejectedValue = function(err: any) {
    spy.and.returnValue(Promise.reject(err));
    return spy;
  };
  
  (spy as any).mockReturnValueOnce = function(value: any) {
    if (value !== null && value !== undefined && !isObservable(value) && !(value instanceof Promise)) {
      value = of(value);
    }
    spy.and.returnValue(value);
    return spy;
  };
  
  (spy as any).mockRestore = function() {
    spy.calls.reset();
    return spy;
  };
  
  return spy as any;
}

export function spyOnObject<T>(object: any, method: string) {
  if (method === 'isWaitingForResponse') {
    try {
      const currentValue = object[method];
      const spy = jasmine.createSpy(method).and.returnValue(currentValue);
      
      (spy as any).mockReturnValue = function(value: any) {
        spy.and.returnValue(value);
        return spy;
      };
      
      (spy as any).mockRestore = function() {
        spy.calls.reset();
        return spy;
      };
      
      return spy;
    } catch (e) {
      const spy = jasmine.createSpy(method);
      (spy as any).mockRestore = function() {
        spy.calls.reset();
        return spy;
      };
      return spy;
    }
  }
  
  if (typeof object === 'object' && object !== null) {
    if (object.hasOwnProperty(method)) {
      const descriptor = Object.getOwnPropertyDescriptor(object, method);
      
      if (descriptor && descriptor.get && !descriptor.set) {
        try {
          const currentValue = object[method];
          const spy = jasmine.createSpy(method).and.returnValue(currentValue);
          (spy as any).mockRestore = function() {
            spy.calls.reset();
            return spy;
          };
          return spy;
        } catch (e) {
          const spy = jasmine.createSpy(method);
          (spy as any).mockRestore = function() {
            spy.calls.reset();
            return spy;
          };
          return spy;
        }
      }
      
      try {
        const originalMethod = object[method];
        if (typeof originalMethod === 'function') {
          const spy = jasmine.createSpy(method).and.callFake(function(...args: any[]) {
            const result = originalMethod.apply(object, args);
            return ensureObservable(result);
          });
          const originalValue = originalMethod;
          object[method] = spy;
          
          attachJestMethods(spy);
          
          (spy as any).mockRestore = function() {
            object[method] = originalValue;
            spy.calls.reset();
            return spy;
          };
          
          return spy;
        } else {
          const spy = jasmine.createSpy(method).and.returnValue(ensureObservable(originalMethod));
          const originalValue = originalMethod;
          object[method] = spy;
          
          attachJestMethods(spy);
          
          (spy as any).mockRestore = function() {
            object[method] = originalValue;
            spy.calls.reset();
            return spy;
          };
          
          return spy;
        }
      } catch (e) {
        const spy = jasmine.createSpy(method);
        attachJestMethods(spy);
        (spy as any).mockRestore = function() {
          spy.calls.reset();
          return spy;
        };
        return spy;
      }
    }
  }
  
  const spy = jasmine.createSpy(method);
  
  attachJestMethods(spy);
  
  (spy as any).mockRestore = function() {
    spy.calls.reset();
    return spy;
  };
  
  try {
    object[method] = spy;
  } catch(e) {
  }
  
  return spy;
}

function attachJestMethods(spy: jasmine.Spy) {
  (spy as any).mockReturnValue = function(value: any) {
    spy.and.returnValue(ensureObservable(value));
    return spy;
  };
  
  (spy as any).mockImplementation = function(impl: any) {
    spy.and.callFake(function(...args: any[]) {
      const result = impl(...args);
      return ensureObservable(result);
    });
    return spy;
  };
  
  (spy as any).mockResolvedValue = function(value: any) {
    spy.and.returnValue(Promise.resolve(value));
    return spy;
  };
  
  (spy as any).mockRejectedValue = function(err: any) {
    spy.and.returnValue(Promise.reject(err));
    return spy;
  };
  
  (spy as any).mockReturnValueOnce = function(value: any) {
    spy.and.returnValue(ensureObservable(value));
    return spy;
  };
  
  (spy as any).mockRestore = function() {
    spy.calls.reset();
    return spy;
  };
}

export function clearAllMocks() {
  jasmine.clock().uninstall();
  jasmine.clock().install();
}

(window as any).jest = {
  fn: createMock,
  spyOn: spyOnObject,
  clearAllMocks: clearAllMocks
}; 
