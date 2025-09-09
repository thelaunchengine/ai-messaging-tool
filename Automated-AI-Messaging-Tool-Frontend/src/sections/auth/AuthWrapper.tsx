'use client';

import { ReactNode } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';

interface AuthWrapperProps {
  children: ReactNode;
}

const AuthWrapper = ({ children }: AuthWrapperProps) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default'
      }}
    >
      <Grid container spacing={2} alignItems="center" justifyContent="center">
        <Grid item xs={12} sm={8} md={6} lg={4}>
          {children}
        </Grid>
      </Grid>
    </Box>
  );
};

export default AuthWrapper;
