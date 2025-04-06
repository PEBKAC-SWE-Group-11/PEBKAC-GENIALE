// This file is required by karma.conf.js and loads recursively all the .spec and framework files

import 'zone.js/testing';
import { getTestBed } from '@angular/core/testing';
import {
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting
} from '@angular/platform-browser-dynamic/testing';

// Importiamo gli helper per Jest
import './app/Test/test-helpers';

// Inizializzazione dell'ambiente di test Angular
getTestBed().initTestEnvironment(
  BrowserDynamicTestingModule,
  platformBrowserDynamicTesting(),
);

// Questo consente di usare jest.fn() e jest.spyOn() nei file di test
(window as any).global = window; 