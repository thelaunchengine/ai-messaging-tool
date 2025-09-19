'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { Box } from '@mui/system';
import Button from '@mui/material/Button';
import FormHelperText from '@mui/material/FormHelperText';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import { Visibility, VisibilityOff, AdminPanelSettings, Person } from '@mui/icons-material';

// project imports
import MainCard from '../../components/MainCard';

// ==============================|| LOGIN ||============================== //

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  };

  const handleSubmit = async (values: { email: string; password: string }) => {
    setIsLoading(true);
    setError('');

    try {
      // Call the authentication API
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: values.email,
          password: values.password
        })
      });

      const data = await response.json();

      if (data.success) {
        // Store user data in localStorage
        if (data.user.role === 'ADMIN') {
          localStorage.setItem('adminToken', data.token);
          localStorage.setItem('adminUser', JSON.stringify(data.user));
          router.push('/admin/dashboard');
        } else {
          localStorage.setItem('userToken', data.token);
          localStorage.setItem('user', JSON.stringify(data.user));
          router.push('/dashboard');
        }
      } else {
        setError(data.error || 'Invalid email or password');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const formik = useFormik({
    initialValues: {
      email: '',
      password: ''
    },
    validationSchema: Yup.object({
      email: Yup.string().email('Invalid email address').required('Email is required'),
      password: Yup.string().min(6, 'Password must be at least 6 characters').required('Password is required')
    }),
    onSubmit: handleSubmit
  });

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#ffffff',
        padding: 2
      }}
    >
      <Box
        sx={{
          width: '100%',
          maxWidth: 400,
          backgroundColor: '#ffffff',
          borderRadius: 3,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          padding: 4
        }}
      >
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography 
            variant="h4" 
            component="h1" 
            sx={{ 
              fontWeight: 700,
              color: '#333333',
              fontSize: '2rem',
              mb: 3
            }}
          >
            Login
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={formik.handleSubmit}>
          <Stack spacing={3}>
            <TextField
              fullWidth
              id="email"
              name="email"
              placeholder="Email Address"
              value={formik.values.email}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.email && Boolean(formik.errors.email)}
              helperText={formik.touched.email && formik.errors.email}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#F5F5F5',
                  borderRadius: 2,
                  '& fieldset': {
                    borderColor: '#DDDDDD',
                    borderWidth: 1
                  },
                  '&:hover fieldset': {
                    borderColor: '#DDDDDD'
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#6A5ACD'
                  }
                },
                '& .MuiInputBase-input': {
                  padding: '14px 16px',
                  color: '#333333',
                  '&::placeholder': {
                    color: '#888888',
                    opacity: 1
                  }
                }
              }}
            />

            <TextField
              fullWidth
              id="password"
              name="password"
              placeholder="Password"
              type={showPassword ? 'text' : 'password'}
              value={formik.values.password}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.password && Boolean(formik.errors.password)}
              helperText={formik.touched.password && formik.errors.password}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleClickShowPassword}
                      onMouseDown={handleMouseDownPassword}
                      edge="end"
                      sx={{ color: '#666666' }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#F5F5F5',
                  borderRadius: 2,
                  '& fieldset': {
                    borderColor: '#DDDDDD',
                    borderWidth: 1
                  },
                  '&:hover fieldset': {
                    borderColor: '#DDDDDD'
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#6A5ACD'
                  }
                },
                '& .MuiInputBase-input': {
                  padding: '14px 16px',
                  color: '#333333',
                  '&::placeholder': {
                    color: '#888888',
                    opacity: 1
                  }
                }
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={isLoading}
              sx={{ 
                mt: 2, 
                py: 2,
                backgroundColor: '#6A5ACD',
                borderRadius: 2,
                fontSize: '1rem',
                fontWeight: 600,
                textTransform: 'none',
                '&:hover': {
                  backgroundColor: '#5A4FCF'
                },
                '&:disabled': {
                  backgroundColor: '#CCCCCC'
                }
              }}
            >
              {isLoading ? <CircularProgress size={24} color="inherit" /> : 'Login'}
            </Button>
          </Stack>
        </form>
      </Box>
    </Box>
  );
};

export default LoginPage;
