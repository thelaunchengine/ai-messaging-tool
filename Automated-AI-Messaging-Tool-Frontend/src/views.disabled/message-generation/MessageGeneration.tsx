'use client';

import { useState } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import Divider from '@mui/material/Divider';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';

// project-imports
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

// assets
import { MessageQuestion, Setting2 } from '@wandersonalwes/iconsax-react';

// ==============================|| MESSAGE GENERATION ||============================== //

export default function MessageGeneration() {
  const theme = useTheme();
  const [aiModel, setAiModel] = useState('gpt-4');
  const [messageType, setMessageType] = useState('general');
  const [customPrompt, setCustomPrompt] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedMessage, setGeneratedMessage] = useState<any>(null);
  const [sampleWebsite, setSampleWebsite] = useState({
    company_name: 'Sample Company',
    industry: 'Technology',
    business_type: 'SaaS',
    about_us_content: 'We are a leading technology company specializing in innovative solutions for modern businesses.'
  });

  const handleAiModelChange = (event: any) => {
    setAiModel(event.target.value);
  };

  const handleMessageTypeChange = (event: any) => {
    setMessageType(event.target.value);
  };

  const handleReset = () => {
    setAiModel('gpt-4');
    setMessageType('general');
    setCustomPrompt('');
    setGeneratedMessage(null);
    setError('');
    setSuccess('');
  };

  const generateMessage = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    setGeneratedMessage(null);

    try {
      // Call the AI generation API with sample data
      const response = await fetch('/api/message-generation/generate-for-selected', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          website_ids: ['sample_website'], // Sample website ID
          message_type: messageType,
          ai_model: aiModel,
          custom_prompt: customPrompt,
          sample_data: sampleWebsite, // Send sample data for generation
          user_id: 'default_user'
        })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.results && result.results.length > 0) {
          setGeneratedMessage(result.results[0]);
          setSuccess('Message generated successfully!');
        } else {
          setError('No message was generated');
        }
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
    <Grid container spacing={GRID_COMMON_SPACING}>
      <Grid size={12}>
        <MainCard title="Message Generation Settings">
          <Stack spacing={3}>
            <Alert severity="info">
              Configure your AI model and message generation settings. You can choose between different AI models and customize the message
              type and prompt templates.
            </Alert>

            <Grid container spacing={3}>
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

              <TextField
                fullWidth
                multiline
                rows={4}
                label="Custom Prompt"
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Enter your custom prompt template here..."
                helperText="Use {website} and {business_type} as placeholders in your prompt"
              />

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

            <Stack direction="row" spacing={2}>
              <Button variant="outlined" onClick={handleReset}>
                Reset to Default
              </Button>
              <Button 
                variant="contained" 
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

      <Grid xs={12} md={6}>
        <MainCard title="AI Generated Message">
          <Stack spacing={3}>
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
                
                <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
                  {generatedMessage.content}
                </Typography>

                {generatedMessage.error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {generatedMessage.error}
                  </Alert>
                )}
              </Paper>
            ) : (
              <Paper variant="outlined" sx={{ p: 3, textAlign: 'center', color: 'text.secondary' }}>
                <Typography variant="body1">
                  {loading ? 'Generating AI message...' : 'Click "Generate AI Message" to create a personalized message using the selected AI model and configuration.'}
                </Typography>
              </Paper>
            )}

            <Stack direction="row" spacing={2}>
              <Button 
                variant="outlined" 
                onClick={generateMessage}
                disabled={loading}
              >
                Regenerate Message
              </Button>
              <Button 
                variant="contained" 
                disabled={!generatedMessage || loading}
              >
                Use This Message
              </Button>
            </Stack>
          </Stack>
        </MainCard>
      </Grid>
    </Grid>
  );
}
