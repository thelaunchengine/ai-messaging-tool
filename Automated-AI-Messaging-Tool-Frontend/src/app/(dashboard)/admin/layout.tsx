'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import DashboardLayout from '../../../layout/DashboardLayout';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return;
    if ((!session?.user || session.user.role !== 'ADMIN') && window.location.pathname !== '/login') {
      router.push('/login');
    }
  }, [session, status, router]);

  if (status === 'loading' || !session?.user || session.user.role !== 'ADMIN') {
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

  return <DashboardLayout>{children}</DashboardLayout>;
}
