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
import Link from '@mui/material/Link';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import { Visibility, VisibilityOff } from '@mui/icons-material';

// project imports
import MainCard from '../../../components/MainCard';
import AuthWrapper from '../../../sections/auth/AuthWrapper';

const Register = () => {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
      confirmPassword: '',
      username: '',
      name: '',
      submit: null
    },
    validationSchema: Yup.object().shape({
      email: Yup.string().email('Must be a valid email').max(255).required('Email is required'),
      password: Yup.string().min(8, 'Password must be at least 8 characters').required('Password is required'),
      confirmPassword: Yup.string()
        .oneOf([Yup.ref('password')], 'Passwords must match')
        .required('Confirm password is required'),
      username: Yup.string()
        .min(3, 'Username must be at least 3 characters')
        .max(20, 'Username must be less than 20 characters')
        .required('Username is required'),
      name: Yup.string()
        .min(2, 'Name must be at least 2 characters')
        .max(50, 'Name must be less than 50 characters')
        .required('Name is required')
    }),
    onSubmit: async (values, { setErrors, setStatus, setSubmitting }) => {
      try {
        setLoading(true);
        setError('');
        setSuccess('');

        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: values.email,
            password: values.password,
            confirmPassword: values.confirmPassword,
            username: values.username,
            name: values.name
          })
        });

        const data = await response.json();

        if (response.ok) {
          setSuccess('Registration successful! Redirecting to login...');
          setTimeout(() => {
            router.push('/login');
          }, 2000);
        } else {
          const errorMessage = data.error || 'Registration failed';
          const details = data.details ? `: ${data.details}` : '';
          setError(errorMessage + details);
          setStatus({ success: false });
          setErrors({ submit: errorMessage + details });
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
              <Typography variant="h3">Sign up</Typography>
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
                id="name"
                name="name"
                label="Full Name"
                value={formik.values.name}
                onChange={formik.handleChange}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
                disabled={loading}
              />
              <TextField
                fullWidth
                id="username"
                name="username"
                label="Username"
                value={formik.values.username}
                onChange={formik.handleChange}
                error={formik.touched.username && Boolean(formik.errors.username)}
                helperText={formik.touched.username && formik.errors.username}
                disabled={loading}
              />
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
              <TextField
                fullWidth
                id="confirmPassword"
                name="confirmPassword"
                label="Confirm Password"
                type={showConfirmPassword ? 'text' : 'password'}
                value={formik.values.confirmPassword}
                onChange={formik.handleChange}
                error={formik.touched.confirmPassword && Boolean(formik.errors.confirmPassword)}
                helperText={formik.touched.confirmPassword && formik.errors.confirmPassword}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowConfirmPassword(!showConfirmPassword)} edge="end" size="large" disabled={loading}>
                        {showConfirmPassword ? <Visibility /> : <VisibilityOff />}
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
              {loading ? 'Creating account...' : 'Sign up'}
            </Button>

            <Stack direction="row" spacing={1} justifyContent="center">
              <Typography variant="body2">Already have an account?</Typography>
              <Link href="/login" variant="body2">
                Sign in
              </Link>
            </Stack>
          </Stack>
        </Box>
      </MainCard>
    </AuthWrapper>
  );
};

export default Register;
