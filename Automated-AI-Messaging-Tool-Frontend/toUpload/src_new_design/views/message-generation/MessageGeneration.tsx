'use client';

import { useState } from 'react';
import {
  Grid,
  Stack,
  Typography,
  Paper,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider,
  Box,
  Chip,
  CircularProgress
} from '@mui/material';
import { useTheme } from '@mui/material';
import MainCard from 'components/MainCard';
import { Setting2, MessageQuestion } from 'lucide-react';

interface GeneratedMessage {
  content: string;
  confidence_score: number;
  message_type: string;
  success: boolean;
  error?: string;
}

export default function MessageGeneration() {
  const theme = useTheme();
  const [aiModel, setAiModel] = useState('gpt-4');
  const [messageType, setMessageType] = useState('inquiry');
  const [customPrompt, setCustomPrompt] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedMessage, setGeneratedMessage] = useState<GeneratedMessage | null>(null);

  const handleAiModelChange = (event: any) => {
    setAiModel(event.target.value);
  };

  const handleMessageTypeChange = (event: any) => {
    setMessageType(event.target.value);
  };

  const handleReset = () => {
    setAiModel('gpt-4');
    setMessageType('inquiry');
    setCustomPrompt('');
    setError('');
    setGeneratedMessage(null);
  };

  const generateMessage = async () => {
    if (!customPrompt && messageType === 'custom') {
      setError('Please enter a custom prompt');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('/api/message-generation/generate-for-selected', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ai_model: aiModel,
          message_type: messageType,
          custom_prompt: customPrompt,
          website_data: {
            company_name: 'Sample Company',
            industry: 'Technology',
            business_type: 'SaaS',
            about_us_content: 'We are a leading technology company specializing in innovative solutions.'
          }
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedMessage(data);
        setSuccess('Message generated successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to generate message');
      }
    } catch (error) {
      setError('Error generating message. Please try again.');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid size={12}>
        <MainCard title="AI Message Generation Settings">
          <Stack spacing={3}>
            <Grid container spacing={2}>
              <Grid size={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>AI Model</InputLabel>
                  <Select value={aiModel} label="AI Model" onChange={handleAiModelChange}>
                    <MenuItem value="gpt-4">GPT-4</MenuItem>
                    <MenuItem value="gpt-3.5">GPT-3.5</MenuItem>
                    <MenuItem value="gemini">Gemini</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid size={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Message Type</InputLabel>
                  <Select value={messageType} label="Message Type" onChange={handleMessageTypeChange}>
                    <MenuItem value="inquiry">General Inquiry</MenuItem>
                    <MenuItem value="partnership">Partnership Proposal</MenuItem>
                    <MenuItem value="support">Support Request</MenuItem>
                    <MenuItem value="custom">Custom</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <Divider />

            <Stack spacing={2}>
              <Stack direction="row" spacing={1} alignItems="center">
                <Setting2 style={{ fontSize: '1.5rem', color: theme.palette.primary.main }} />
                <Typography variant="h6">Prompt Template</Typography>
              </Stack>

              {messageType === 'custom' && (
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Custom Prompt"
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="Enter your custom prompt template here..."
                  helperText="Use {website} and {business_type} as placeholders in your prompt"
                  error={!!error}
                />
              )}

              <Paper variant="outlined" sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Available Variables:
                </Typography>
                <Stack spacing={1}>
                  <Typography variant="body2">• {`{website}`} - Website URL</Typography>
                  <Typography variant="body2">• {`{business_type}`} - Detected business type</Typography>
                  <Typography variant="body2">• {`{company_name}`} - Company name</Typography>
                  <Typography variant="body2">• {`{industry}`} - Industry sector</Typography>
                </Stack>
              </Paper>
            </Stack>

            {error && <Alert severity="error">{error}</Alert>}
            {success && <Alert severity="success">{success}</Alert>}

            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button variant="outlined" color="secondary" onClick={handleReset}>
                Reset to Default
              </Button>
              <Button 
                variant="contained" 
                color="primary"
                onClick={generateMessage}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : null}
              >
                {loading ? 'Generating...' : 'Generate AI Message'}
              </Button>
            </Stack>
          </Stack>
        </MainCard>
      </Grid>

      <Grid size={12}>
        <MainCard title="AI Generated Message">
          <Stack spacing={3}>
            <Stack direction="row" spacing={1} alignItems="center">
              <MessageQuestion style={{ fontSize: '1.5rem', color: theme.palette.primary.main }} />
              <Typography variant="h6">Generated Message</Typography>
            </Stack>

            {generatedMessage ? (
              <Paper variant="outlined" sx={{ p: 3 }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Chip 
                    label={`${messageType.toUpperCase()}`} 
                    color="primary" 
                    size="small" 
                  />
                  <Chip 
                    label={`Confidence: ${(generatedMessage.confidence_score * 100).toFixed(1)}%`} 
                    color={generatedMessage.confidence_score > 0.7 ? 'success' : 'warning'} 
                    size="small" 
                  />
                </Box>
                <Typography variant="body1" paragraph>
                  {generatedMessage.content}
                </Typography>
              </Paper>
            ) : (
              <Paper variant="outlined" sx={{ p: 3 }}>
                <Typography variant="body1" color="text.secondary" align="center">
                  Click "Generate AI Message" to create a personalized message based on your configuration.
                </Typography>
              </Paper>
            )}

            {generatedMessage && (
              <Stack direction="row" spacing={2} justifyContent="flex-end">
                <Button variant="outlined" color="secondary" onClick={generateMessage}>
                  Regenerate
                </Button>
                <Button variant="contained" color="primary">
                  Use This Message
                </Button>
              </Stack>
            )}
          </Stack>
        </MainCard>
      </Grid>
    </Grid>
  );
}
