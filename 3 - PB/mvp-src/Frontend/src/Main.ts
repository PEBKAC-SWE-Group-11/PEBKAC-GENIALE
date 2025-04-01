import { bootstrapApplication } from '@angular/platform-browser';
import { AppConfig } from './app/App.config';
import { AppComponent } from './app/App.component';

bootstrapApplication(AppComponent, AppConfig)
  .catch((err) => console.error(err));
