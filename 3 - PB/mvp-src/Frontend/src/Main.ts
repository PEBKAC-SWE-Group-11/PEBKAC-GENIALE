import { bootstrapApplication } from '@angular/platform-browser';
import { AppConfig } from './App/App.config';
import { AppComponent } from './App/App.component';

bootstrapApplication(AppComponent, AppConfig)
  .catch((err) => console.error(err));
