'use client';

import { useEffect, useState } from 'react';

// next
import { useRouter } from 'next/navigation';

// project-imports
import Loader from 'components/Loader';

// types
import { GuardProps } from 'types/auth';

// ==============================|| AUTH GUARD ||============================== //

export default function AuthGuard({ children }: GuardProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for user authentication (localStorage-based)
    const checkAuth = () => {
      // If we're on the login page, don't check authentication
      if (window.location.pathname === '/login') {
        setIsAuthenticated(false);
        setIsLoading(false);
        return;
      }

      const userToken = localStorage.getItem('userToken');
      const user = localStorage.getItem('user');
      
      if (userToken && user) {
        try {
          const userData = JSON.parse(user);
          if (userData.role === 'user') {
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

  if (isLoading) return <Loader />;
  if (!isAuthenticated) return <Loader />;

  return <>{children}</>;
}
