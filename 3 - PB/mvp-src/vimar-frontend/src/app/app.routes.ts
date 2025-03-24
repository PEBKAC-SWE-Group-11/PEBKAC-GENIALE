import { Routes } from '@angular/router';
import { AdminLoginComponent } from './features/admin/login/login.component';
import { AdminDashboardComponent } from './features/admin/dashboard/dashboard.component';
import { adminGuard } from './core/guards/admin.guard';

export const routes: Routes = [
  { path: 'admin/login', component: AdminLoginComponent },
  { 
    path: 'admin/dashboard', 
    component: AdminDashboardComponent,
    canActivate: [adminGuard]
  },
  { path: 'admin', redirectTo: 'admin/login', pathMatch: 'full' }
];
