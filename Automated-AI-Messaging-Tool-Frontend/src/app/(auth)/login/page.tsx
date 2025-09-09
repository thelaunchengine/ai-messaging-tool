'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { signIn } from 'next-auth/react';
import { useSession } from 'next-auth/react';
import {
  Box,
  Button,
  FormHelperText,
  IconButton,
  InputAdornment,
  Link,
  Stack,
  TextField,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

// project imports
import MainCard from '../../../components/MainCard';
import AuthWrapper from '../../../sections/auth/AuthWrapper';

const Login = () => {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (status !== 'authenticated') return;
    if (session?.user?.role === 'ADMIN' && window.location.pathname !== '/admin/dashboard') {
      router.push('/admin/dashboard');
    } else if (session?.user?.role === 'USER' && window.location.pathname !== '/dashboard') {
      router.push('/dashboard');
    }
  }, [session, status, router]);

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
      submit: null
    },
    validationSchema: Yup.object().shape({
      email: Yup.string().email('Must be a valid email').max(255).required('Email is required'),
      password: Yup.string().min(8, 'Password must be at least 8 characters').required('Password is required')
    }),
    onSubmit: async (values, { setErrors, setStatus, setSubmitting }) => {
      try {
        setLoading(true);
        setError('');
        setSuccess('');

        const response = await signIn('credentials', {
          email: values.email,
          password: values.password,
          redirect: false
        });

        if (response?.error) {
          setError(response.error);
          setStatus({ success: false });
          setErrors({ submit: response.error });
        } else {
          setSuccess('Login successful! Redirecting...');
          // No redirect here; useEffect will handle it
        }
      } catch (err: any) {
        setError('Network error. Please try again.');
        setStatus({ success: false });
        setErrors({ submit: 'Network error. Please try again.' });
      } finally {
        setLoading(false);
        setSubmitting(false);
      }
    }
  });

  return (
    <AuthWrapper>
      <MainCard>
        <Box sx={{ p: 3 }}>
          <Stack spacing={3}>
            <Stack direction="row" spacing={1} alignItems="center" justifyContent="center">
              <Typography variant="h3">Sign in</Typography>
            </Stack>

            {error && (
              <Alert severity="error" onClose={() => setError('')}>
                {error}
              </Alert>
            )}

            {success && (
              <Alert severity="success" onClose={() => setSuccess('')}>
                {success}
              </Alert>
            )}

            <Stack spacing={2}>
              <TextField
                fullWidth
                id="email"
                name="email"
                label="Email Address"
                value={formik.values.email}
                onChange={formik.handleChange}
                error={formik.touched.email && Boolean(formik.errors.email)}
                helperText={formik.touched.email && formik.errors.email}
                disabled={loading}
              />
              <TextField
                fullWidth
                id="password"
                name="password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={formik.values.password}
                onChange={formik.handleChange}
                error={formik.touched.password && Boolean(formik.errors.password)}
                helperText={formik.touched.password && formik.errors.password}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="large" disabled={loading}>
                        {showPassword ? <Visibility /> : <VisibilityOff />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
              />
            </Stack>



            {formik.errors.submit && (
              <FormHelperText error sx={{ mt: 3 }}>
                {formik.errors.submit}
              </FormHelperText>
            )}

            <Stack direction="row" spacing={1} justifyContent="space-between" alignItems="center">
              <Typography variant="body2">
                <Link href="/forgot-password" variant="body2" color="primary">
                  Forgot Password?
                </Link>
              </Typography>
            </Stack>

            <Button
              fullWidth
              size="large"
              type="submit"
              variant="contained"
              color="primary"
              onClick={() => formik.handleSubmit()}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </Button>

            {/* <Stack direction="row" spacing={1} justifyContent="center">
              <Typography variant="body2">Don't have an account?</Typography>
              <Link href="/register" variant="body2">
                Sign up
              </Link>
            </Stack> */}
          </Stack>
        </Box>
      </MainCard>
    </AuthWrapper>
  );
};

export default Login;
