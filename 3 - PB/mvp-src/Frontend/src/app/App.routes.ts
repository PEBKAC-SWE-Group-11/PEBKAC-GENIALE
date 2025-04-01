import { Routes } from '@angular/router';
import { AdminLoginComponent } from './Features/Admin/Login/Login.component';
import { AdminDashboardComponent } from './Features/Admin/Dashboard/Dashboard.component';
import { AdminGuard } from './Core/Guards/Admin.guard';

export const routes: Routes = [
  { path: 'admin/login', component: AdminLoginComponent },
  { 
    path: 'admin/dashboard', 
    component: AdminDashboardComponent,
    canActivate: [AdminGuard]
  },
  { path: 'admin', redirectTo: 'admin/login', pathMatch: 'full' }
];
