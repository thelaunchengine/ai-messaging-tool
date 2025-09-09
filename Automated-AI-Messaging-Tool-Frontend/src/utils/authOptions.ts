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
        try {
          const user = await axios.post('/api/auth/login', {
            password: credentials?.password,
            email: credentials?.email
          });

          if (user) {
            user.data.user.accessToken = user.data.user.id;
            return user.data.user;
          }
        } catch (e: any) {
          // Handle disabled user error specifically
          if (e?.response?.status === 403) {
            throw new Error('Account is disabled. Please contact administrator.');
          }
          
          const errorMessage = e?.message || e?.response?.data?.message || 'Something went wrong!';
          throw new Error(errorMessage);
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
