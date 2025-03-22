import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { CanActivateFn } from '@angular/router';

export const adminGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  
  const token = localStorage.getItem('admin_token');
  const isAuthenticated = localStorage.getItem('admin_authenticated');
  
  if (!token && !isAuthenticated) {
    router.navigate(['/admin/login']);
    return false;
  }
  
  return true;
}; 