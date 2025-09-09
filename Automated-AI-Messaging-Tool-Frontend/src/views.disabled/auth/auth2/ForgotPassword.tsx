'use client';

// next
import Link from 'next/link';

// material-ui
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

// project-imports
import AuthWrapper2 from 'sections/auth/AuthWrapper2';
import AuthForgotPassword from 'sections/auth/auth-forms/AuthForgotPassword';
import useUser from 'hooks/useUser';

// ================================|| FORGOT PASSWORD ||================================ //

export default function ForgotPasswordPage() {
  const user = useUser();

  return (
    <AuthWrapper2>
      <Grid container spacing={3}>
        <Grid size={12}>
          <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'baseline', mb: { xs: -0.5, sm: 0.5 } }}>
            <Typography variant="h3">Forgot Password</Typography>
            <Typography
              component={Link}
              href={user ? '/auth/login2' : '/login2'}
              variant="body1"
              sx={{ textDecoration: 'none' }}
              color="primary"
            >
              Back to Login
            </Typography>
          </Stack>
        </Grid>
        <Grid size={12}>
          <AuthForgotPassword />
        </Grid>
      </Grid>
    </AuthWrapper2>
  );
}
