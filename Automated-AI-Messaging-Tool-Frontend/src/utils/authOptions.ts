// next
import type { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

// project imports
import axios from './axios';


declare module 'next-auth' {
  interface User {
    accessToken?: string;
  }

  interface Session {
    accessToken?: string;
    user: {
      id?: string;
      name?: string;
      email?: string;
    };
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    accessToken?: string;
    id?: string;
    provider?: string;
  }
}

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET,
  providers: [
    CredentialsProvider({
      id: 'login',
      name: 'login',
      credentials: {
        email: { name: 'email', label: 'Email', type: 'email', placeholder: 'Enter Email' },
        password: { name: 'password', label: 'Password', type: 'password', placeholder: 'Enter Password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          // Import PrismaClient directly here to avoid circular dependency
          const { PrismaClient } = await import('@prisma/client');
          const bcrypt = await import('bcryptjs');
          const prisma = new PrismaClient();

          // Find user by email using raw SQL
          const userResult = await prisma.$queryRaw`SELECT * FROM users WHERE email = ${credentials.email.toLowerCase()} LIMIT 1`;
          const user = (userResult as any[])[0];

          if (!user) {
            await prisma.$disconnect();
            return null;
          }

          // Check if user is active
          if (user.status !== 'active') {
            await prisma.$disconnect();
            throw new Error('Account is disabled. Please contact administrator.');
          }
          
          // Verify password
          if (!user.password) {
            await prisma.$disconnect();
            return null;
          }

          const isPasswordValid = await bcrypt.compare(credentials.password, user.password);
          await prisma.$disconnect();

          if (!isPasswordValid) {
            return null;
          }

          return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
            accessToken: user.id
          };
        } catch (error: any) {
          console.error('Auth error:', error);
          if (error.message === 'Account is disabled. Please contact administrator.') {
            throw error;
          }
          return null;
        }
      }
    }),
    CredentialsProvider({
      id: 'register',
      name: 'Register',
      credentials: {
        firstname: { name: 'firstname', label: 'Firstname', type: 'text', placeholder: 'Enter Firstname' },
        lastname: { name: 'lastname', label: 'Lastname', type: 'text', placeholder: 'Enter Lastname' },
        email: { name: 'email', label: 'Email', type: 'email', placeholder: 'Enter Email' },
        company: { name: 'company', label: 'Company', type: 'text', placeholder: 'Enter Company' },
        password: { name: 'password', label: 'Password', type: 'password', placeholder: 'Enter Password' }
      },
      async authorize(credentials) {
        try {
          const user = await axios.post('/api/auth/register', {
            firstName: credentials?.firstname,
            lastName: credentials?.lastname,
            company: credentials?.company,
            password: credentials?.password,
            email: credentials?.email
          });

          if (user) {
            return user.data;
          }
        } catch (e: any) {
          const errorMessage = e?.message || e?.response?.data?.message || 'Something went wrong!';
          throw new Error(errorMessage);
        }
      }
    })
  ],
  callbacks: {
    jwt: async ({ token, user, account }) => {
      if (user) {
        token.accessToken = user.accessToken;
        token.id = user.id;
        token.provider = account?.provider;
        token.role = user.role; // Add role to JWT
      }
      return token;
    },
    session: ({ session, token }) => {
      if (token) {
        session.user = session.user || {};
        session.user.id = token.id as string;
        session.accessToken = token.accessToken as string;
        session.user.role = token.role as string; // Add role to session
      }
      return session;
    },
    async signIn(params) {
      // Prevent JWT token issuance on registration
      if (params.account?.provider === 'register') {
        return `${process.env.NEXTAUTH_URL}/login`;
      }
      return true;
    },
    async redirect({ url, baseUrl }) {
      // Use the correct base URL from environment
      const correctBaseUrl = process.env.NEXTAUTH_URL || baseUrl;
      
      // Allows relative callback URLs
      if (url.startsWith("/")) return `${correctBaseUrl}${url}`;
      // Allows callback URLs on the same origin
      else if (new URL(url).origin === correctBaseUrl) return url;
      return `${correctBaseUrl}/dashboard`;
    }
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60 // 30 days
  },
  pages: {
    signIn: '/login',
    newUser: '/register'
  }
};
