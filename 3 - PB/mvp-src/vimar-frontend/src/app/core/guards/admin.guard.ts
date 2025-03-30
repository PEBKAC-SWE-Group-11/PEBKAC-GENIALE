import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { CanActivateFn } from '@angular/router';

export const adminGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  
  const token = localStorage.getItem('adminToken');
  const isAuthenticated = localStorage.getItem('adminAuthenticated');
  
  if (!token && !isAuthenticated) {
    router.navigate(['/admin/login']);
    return false;
  }
  
  return true;
}; 