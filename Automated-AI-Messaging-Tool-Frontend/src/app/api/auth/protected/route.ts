// next
import { getServerSession } from 'next-auth';
import { NextResponse } from 'next/server';

// project-imports
import { authOptions } from 'utils/authOptions';

// ==============================|| NEXT AUTH - ROUTES  ||============================== //

export async function GET() {
  const session = await getServerSession(authOptions);
  if (session && session.user?.role === 'ADMIN') {
    return NextResponse.json({ protected: true });
  } else {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
  }
}
