import { Routes } from '@angular/router';
import { AdminLoginComponent } from './admin/admin-login/admin-login.component';
import { AdminDashboardComponent } from './admin/admin-dashboard/admin-dashboard.component';
import { adminGuard } from './guards/admin.guard';

export const routes: Routes = [
  { path: 'admin/login', component: AdminLoginComponent },
  { 
    path: 'admin/dashboard', 
    component: AdminDashboardComponent,
    canActivate: [adminGuard]
  },
  { path: 'admin', redirectTo: 'admin/login', pathMatch: 'full' }
];
