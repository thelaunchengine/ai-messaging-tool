import NextAuth from 'next-auth';
import { authOptions } from '../../_lib/auth';

// ==============================|| NEXT AUTH - ROUTES  ||============================== //

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
