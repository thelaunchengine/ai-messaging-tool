// next
const { NextAuthOptions } = require('next-auth');
const CredentialsProvider = require("next-auth/providers/credentials").default;

// project imports
const axios = require('./axios');

module.exports = {
  authOptions: {
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
          } catch (e) {
            if (e?.response?.status === 403) {
              throw new Error('Account is disabled. Please contact administrator.');
            }
            
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
          token.role = user.role;
        }
        return token;
      },
      session: ({ session, token }) => {
        if (token) {
          session.user = session.user || {};
          session.user.id = token.id;
          session.accessToken = token.accessToken;
          session.user.role = token.role;
        }
        return session;
      }
    },
    session: {
      strategy: 'jwt',
      maxAge: 30 * 24 * 60 * 60
    },
    pages: {
      signIn: '/login',
      newUser: '/register'
    }
  }
};
