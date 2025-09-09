'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import FormHelperText from '@mui/material/FormHelperText';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import { Visibility, VisibilityOff, AdminPanelSettings } from '@mui/icons-material';

// project imports
import MainCard from '../../../../components/MainCard';
import AuthWrapper from '../../../../sections/auth/AuthWrapper';

const AdminLogin = () => {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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

        // Mock admin authentication - replace with actual API call
        if (values.email === 'admin@example.com' && values.password === 'admin123') {
          setSuccess('Login successful! Redirecting...');
          // Store admin session
          localStorage.setItem('adminToken', 'mock-admin-token');
          localStorage.setItem(
            'adminUser',
            JSON.stringify({
              id: 'admin-1',
              email: values.email,
              role: 'admin'
            })
          );
          setTimeout(() => {
            router.push('/admin/dashboard');
          }, 1000);
        } else {
          setError('Invalid admin credentials');
          setStatus({ success: false });
          setErrors({ submit: 'Invalid admin credentials' });
        }
      } catch (err: any) {
        setError('Login failed. Please try again.');
        setStatus({ success: false });
        setErrors({ submit: 'Login failed. Please try again.' });
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
              <AdminPanelSettings sx={{ fontSize: 40, color: 'primary.main' }} />
              <Typography variant="h3">Admin Sign in</Typography>
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
                label="Admin Email"
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
              {loading ? 'Signing in...' : 'Sign in as Admin'}
            </Button>

            <Stack direction="row" spacing={1} justifyContent="center">
              <Typography variant="body2" color="text.secondary">
                Demo: admin@example.com / admin123
              </Typography>
            </Stack>
          </Stack>
        </Box>
      </MainCard>
    </AuthWrapper>
  );
};

export default AdminLogin;
