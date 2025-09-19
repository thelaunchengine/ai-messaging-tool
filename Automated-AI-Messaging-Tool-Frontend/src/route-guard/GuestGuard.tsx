'use client';

import { useEffect } from 'react';

// next
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';

// project-imports
import Loader from 'components/Loader';
import { useIspValue } from 'hooks/useIspValue';

// types
import { GuardProps } from 'types/auth';

// ==============================|| GUEST GUARD ||============================== //

export default function GuestGuard({ children }: GuardProps) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const ispValueAvailable = useIspValue();
  useEffect(() => {
    if (status !== 'authenticated') return;
    if (session?.user?.role === 'ADMIN' && window.location.pathname !== '/admin/dashboard') {
      router.push('/admin/dashboard');
    } else if (session?.user?.role === 'USER' && window.location.pathname !== '/dashboard') {
      router.push(ispValueAvailable ? '/dashboard?isp=1' : '/dashboard');
    }
  }, [session, status, router]);

  if (status === 'loading' || session?.user) return <Loader />;

  return <>{children}</>;
}
