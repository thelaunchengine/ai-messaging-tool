'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function TestAdminAuth() {
  const router = useRouter();

  useEffect(() => {
    // Set admin authentication in localStorage
    const adminUser = {
      id: 'admin-1',
      email: 'admin@example.com',
      name: 'Admin User',
      role: 'ADMIN'
    };
    
    localStorage.setItem('adminUser', JSON.stringify(adminUser));
    localStorage.setItem('adminToken', 'test-admin-token');
    
    // Redirect to admin dashboard
    router.push('/admin/dashboard');
  }, [router]);

  return (
    <div style={{ padding: '20px' }}>
      <h1>Setting up admin authentication...</h1>
      <p>Redirecting to admin dashboard...</p>
    </div>
  );
}
