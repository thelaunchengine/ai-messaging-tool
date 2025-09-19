'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const adminToken = localStorage.getItem('adminToken');
    const userToken = localStorage.getItem('userToken');
    
    if (adminToken || userToken) {
      // User is logged in, redirect to appropriate dashboard
      if (adminToken) {
        router.push('/admin/dashboard');
      } else {
        router.push('/dashboard');
      }
    } else {
      // User is not logged in, redirect to login
      router.push('/login');
    }
  }, [router]);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      fontSize: '18px'
    }}>
      Redirecting...
    </div>
  );
}
