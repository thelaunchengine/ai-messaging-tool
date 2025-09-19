'use client';

import { useEffect } from 'react';

// next
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';

// project-imports
import Loader from 'components/Loader';

// types
import { GuardProps } from 'types/auth';

// ==============================|| AUTH GUARD ||============================== //

export default function AuthGuard({ children }: GuardProps) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return;
    if (!session?.user || session.user.role !== 'USER') {
      router.push('/login');
    }
  }, [session, status, router]);

  if (status === 'loading' || !session?.user || session.user.role !== 'USER') return <Loader />;

  return <>{children}</>;
}
