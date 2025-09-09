'use client';

import { useState } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Checkbox from '@mui/material/Checkbox';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';

// ==============================|| CONTACT FORM ||============================== //

export default function ContactForm() {
  const theme = useTheme();
  const [size, setSize] = useState(1);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    company: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Send form data to API
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setSuccess(true);
        // Reset form
        setFormData({
          firstName: '',
          lastName: '',
          email: '',
          phone: '',
          company: '',
          message: ''
        });
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to submit form. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Alert severity="success" sx={{ mb: 3 }}>
          Thank you for your message! We have received your inquiry and will respond within 24 hours.
        </Alert>
        <Typography variant="h5" gutterBottom>
          Confirmation Email Sent
        </Typography>
        <Typography color="textSecondary" paragraph>
          We've sent a confirmation email to {formData.email} confirming your submission.
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => setSuccess(false)}
          sx={{ mt: 2 }}
        >
          Send Another Message
        </Button>
      </Box>
    );
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid size={6}>
          <TextField
            fullWidth
            label="First Name"
            name="firstName"
            value={formData.firstName}
            onChange={handleInputChange}
            required
            size="small"
          />
        </Grid>
        <Grid size={6}>
          <TextField
            fullWidth
            label="Last Name"
            name="lastName"
            value={formData.lastName}
            onChange={handleInputChange}
            required
            size="small"
          />
        </Grid>
        <Grid size={12}>
          <TextField
            fullWidth
            label="Email Address"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleInputChange}
            required
            size="small"
          />
        </Grid>
        <Grid size={6}>
          <TextField
            fullWidth
            label="Phone Number"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            size="small"
          />
        </Grid>
        <Grid size={6}>
          <TextField
            fullWidth
            label="Company"
            name="company"
            value={formData.company}
            onChange={handleInputChange}
            size="small"
          />
        </Grid>
        <Grid size={12}>
          <TextField
            fullWidth
            label="Message"
            name="message"
            multiline
            rows={4}
            value={formData.message}
            onChange={handleInputChange}
            required
            size="small"
            inputProps={{ maxLength: 1000 }}
            helperText={`${formData.message.length}/1000 characters`}
          />
        </Grid>
        <Grid size={12}>
          <Stack direction="row" sx={{ alignItems: 'center', ml: -1 }}>
            <Checkbox sx={{ '& .css-1vjb4cj': { borderRadius: '2px' } }} defaultChecked required />
            <Typography>
              I agree to all the{' '}
              <Typography component="span" sx={{ color: 'primary.main', cursor: 'pointer' }}>
                Terms & Condition
              </Typography>
            </Typography>
          </Stack>
        </Grid>
        <Grid size={12}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <Button 
            variant="contained" 
            fullWidth 
            type="submit"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Sending...' : 'Submit'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}
