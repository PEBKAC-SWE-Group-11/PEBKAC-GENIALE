/**
 * Helper functions to replace Jest functions with Jasmine equivalents
 */

import { Observable, of } from 'rxjs';

// Verificare se un valore è un Observable
function isObservable(value: any): boolean {
  return value && typeof value.subscribe === 'function';
}

// Convertire un valore in Observable se necessario
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

// Rimpiazzare jest.fn()
export function createMock<T = any>() {
  const spy = jasmine.createSpy();
  
  // Aggiungiamo i metodi di mock simili a Jest
  (spy as any).mockReturnValue = function(value: any) {
    // Assicuriamo che il valore restituito sia un Observable se necessario
    if (value !== null && value !== undefined && !isObservable(value) && !(value instanceof Promise)) {
      value = of(value);
    }
    spy.and.returnValue(value);
    return spy;
  };
  
  (spy as any).mockImplementation = function(impl: any) {
    spy.and.callFake(function(...args: any[]) {
      const result = impl(...args);
      // Assicuriamo che il risultato dell'implementazione sia un Observable se necessario
      if (result !== null && result !== undefined && !isObservable(result) && !(result instanceof Promise)) {
        return of(result);
      }
      return result;
    });
    return spy;
  };
  
  // Support for Promise returns (Jest specific)
  (spy as any).mockResolvedValue = function(value: any) {
    spy.and.returnValue(Promise.resolve(value));
    return spy;
  };
  
  (spy as any).mockRejectedValue = function(err: any) {
    spy.and.returnValue(Promise.reject(err));
    return spy;
  };
  
  // Support for Observable returns (Angular specific)
  (spy as any).mockReturnValueOnce = function(value: any) {
    // Assicuriamo che il valore restituito sia un Observable se necessario
    if (value !== null && value !== undefined && !isObservable(value) && !(value instanceof Promise)) {
      value = of(value);
    }
    spy.and.returnValue(value);
    return spy;
  };
  
  // Supporto per mockRestore
  (spy as any).mockRestore = function() {
    // In Jasmine, non c'è un equivalente diretto, ma possiamo resettare la spy
    spy.calls.reset();
    return spy;
  };
  
  return spy as any;
}

// Rimpiazzare jest.spyOn()
export function spyOnObject<T>(object: any, method: string) {
  // Caso speciale: proprietà isWaitingForResponse
  if (method === 'isWaitingForResponse') {
    // Invece di sovrascrivere il getter, creiamo una spy che intercetta
    // le chiamate al getter ma mantiene il comportamento originale
    try {
      // Ottieni il valore attuale
      const currentValue = object[method];
      // Crea una spy che restituisce il valore
      const spy = jasmine.createSpy(method).and.returnValue(currentValue);
      
      // Aggiungi metodi di modifica sicuri che non cercano di sovrascrivere il getter
      (spy as any).mockReturnValue = function(value: any) {
        spy.and.returnValue(value);
        return spy;
      };
      
      // Supporto per mockRestore
      (spy as any).mockRestore = function() {
        spy.calls.reset();
        return spy;
      };
      
      return spy;
    } catch (e) {
      // Fallback: crea un nuovo spy
      const spy = jasmine.createSpy(method);
      (spy as any).mockRestore = function() {
        spy.calls.reset();
        return spy;
      };
      return spy;
    }
  }
  
  // Per altre proprietà, tentativo standard
  if (typeof object === 'object' && object !== null) {
    if (object.hasOwnProperty(method)) {
      // Verifichiamo se è un getter
      const descriptor = Object.getOwnPropertyDescriptor(object, method);
      
      if (descriptor && descriptor.get && !descriptor.set) {
        try {
          // In caso di getter senza setter, otteniamo il valore attuale
          const currentValue = object[method];
          // Crea una spy che restituisce il valore attuale
          const spy = jasmine.createSpy(method).and.returnValue(currentValue);
          // Aggiungiamo mockRestore
          (spy as any).mockRestore = function() {
            spy.calls.reset();
            return spy;
          };
          return spy;
        } catch (e) {
          // Se l'accesso al getter fallisce, crea un nuovo spy
          const spy = jasmine.createSpy(method);
          // Aggiungiamo mockRestore
          (spy as any).mockRestore = function() {
            spy.calls.reset();
            return spy;
          };
          return spy;
        }
      }
      
      // Se non è un getter, usiamo un mock tradizionale
      try {
        const originalMethod = object[method];
        // Se è una funzione, creiamo uno spy che la emula
        if (typeof originalMethod === 'function') {
          const spy = jasmine.createSpy(method).and.callFake(function(...args: any[]) {
            const result = originalMethod.apply(object, args);
            // Assicuriamo che il risultato sia un Observable se necessario
            return ensureObservable(result);
          });
          // Sovrascriviamo il metodo con lo spy
          const originalValue = originalMethod;
          object[method] = spy;
          
          // Aggiungiamo metodi speciali di Jest
          attachJestMethods(spy);
          
          // Per mockRestore, ripristiniamo il valore originale
          (spy as any).mockRestore = function() {
            object[method] = originalValue;
            spy.calls.reset();
            return spy;
          };
          
          return spy;
        } else {
          // Se è un valore, creiamo uno spy che lo restituisce
          const spy = jasmine.createSpy(method).and.returnValue(ensureObservable(originalMethod));
          const originalValue = originalMethod;
          object[method] = spy;
          
          // Aggiungiamo metodi speciali di Jest
          attachJestMethods(spy);
          
          // Per mockRestore, ripristiniamo il valore originale
          (spy as any).mockRestore = function() {
            object[method] = originalValue;
            spy.calls.reset();
            return spy;
          };
          
          return spy;
        }
      } catch (e) {
        // Se l'accesso al metodo fallisce, crea un nuovo spy
        const spy = jasmine.createSpy(method);
        attachJestMethods(spy);
        // Aggiungiamo mockRestore
        (spy as any).mockRestore = function() {
          spy.calls.reset();
          return spy;
        };
        return spy;
      }
    }
  }
  
  // Se non esiste o non possiamo accedervi, creiamo un nuovo spy
  const spy = jasmine.createSpy(method);
  
  // Per gestire le chiamate a mockResolvedValue nei test esistenti
  attachJestMethods(spy);
  
  // Aggiungiamo mockRestore
  (spy as any).mockRestore = function() {
    spy.calls.reset();
    return spy;
  };
  
  // Tentiamo di assegnare lo spy (può fallire se è un getter-only)
  try {
    object[method] = spy;
  } catch(e) {
    // Ignoriamo l'errore se non possiamo assegnare
  }
  
  return spy;
}

// Aggiungi metodi di Jest allo spy
function attachJestMethods(spy: jasmine.Spy) {
  // supporto per mockReturnValue
  (spy as any).mockReturnValue = function(value: any) {
    spy.and.returnValue(ensureObservable(value));
    return spy;
  };
  
  // Supporto per mockImplementation
  (spy as any).mockImplementation = function(impl: any) {
    spy.and.callFake(function(...args: any[]) {
      const result = impl(...args);
      return ensureObservable(result);
    });
    return spy;
  };
  
  // Supporto per promise (mockResolvedValue)
  (spy as any).mockResolvedValue = function(value: any) {
    spy.and.returnValue(Promise.resolve(value));
    return spy;
  };
  
  // Supporto per promise rejections
  (spy as any).mockRejectedValue = function(err: any) {
    spy.and.returnValue(Promise.reject(err));
    return spy;
  };
  
  // Supporto per Observable (usato in Angular)
  (spy as any).mockReturnValueOnce = function(value: any) {
    spy.and.returnValue(ensureObservable(value));
    return spy;
  };
  
  // Supporto per mockRestore
  (spy as any).mockRestore = function() {
    spy.calls.reset();
    return spy;
  };
}

// Rimpiazzare jest.clearAllMocks()
export function clearAllMocks() {
  jasmine.clock().uninstall();
  jasmine.clock().install();
}

// Rendere disponibili le funzioni globalmente
(window as any).jest = {
  fn: createMock,
  spyOn: spyOnObject,
  clearAllMocks: clearAllMocks
}; 