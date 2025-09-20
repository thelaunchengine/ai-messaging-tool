'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import DashboardLayout from '../../../layout/DashboardLayout';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for admin authentication (localStorage-based)
    const checkAuth = () => {
      // If we're on the login page, don't check authentication
      if (window.location.pathname === '/login') {
        setIsAuthenticated(false);
        setIsLoading(false);
        return;
      }

      // For testing purposes, temporarily bypass authentication
      // TODO: Re-enable authentication in production
      // setIsAuthenticated(true);
      // setIsLoading(false);
      // return;

      const adminToken = localStorage.getItem('adminToken');
      const adminUser = localStorage.getItem('adminUser');
      
      if (adminToken && adminUser) {
        try {
          const user = JSON.parse(adminUser);
          if (user.role === 'ADMIN' || user.role === 'admin') {
            setIsAuthenticated(true);
            setIsLoading(false);
            return;
          }
        } catch (e) {
          // Invalid user data
        }
      }
      
      // Not authenticated - redirect to login
      router.push('/login');
      setIsLoading(false);
    };

    checkAuth();
  }, [router]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          flexDirection: 'column',
          gap: '16px'
        }}
      >
        <div>Loading...</div>
        <div>Verifying admin access...</div>
      </div>
    );
  }

  // If not authenticated, show the children (login page) without the dashboard layout
  if (!isAuthenticated) {
    return <>{children}</>;
  }

  return <DashboardLayout>{children}</DashboardLayout>;
}
