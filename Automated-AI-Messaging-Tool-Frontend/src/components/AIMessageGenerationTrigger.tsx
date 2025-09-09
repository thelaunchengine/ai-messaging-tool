'use client';

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  Stack,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  Psychology as AiIcon,
  PlayArrow as PlayIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

interface AIMessageGenerationTriggerProps {
  fileUploadId: string;
  totalWebsites: number;
  onGenerationComplete?: () => void;
}

export default function AIMessageGenerationTrigger({
  fileUploadId,
  totalWebsites,
  onGenerationComplete
}: AIMessageGenerationTriggerProps) {
  const [messageType, setMessageType] = useState('general');
  const [customPrompt, setCustomPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [generationStatus, setGenerationStatus] = useState<'idle' | 'generating' | 'completed' | 'failed'>('idle');

  const handleGenerateMessages = async () => {
    if (messageType === 'custom' && !customPrompt.trim()) {
      setError('Please enter a custom prompt for custom message type');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    setGenerationStatus('generating');

    try {
      const response = await fetch('/api/workflow/trigger-ai-generation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileUploadId,
          messageType,
          customPrompt: customPrompt.trim(),
          aiModel: 'gemini'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(`AI message generation started successfully! Task ID: ${data.task_id}\n\nGenerating personalized messages for ${totalWebsites} websites using Gemini AI.`);
        setGenerationStatus('completed');
        
        if (onGenerationComplete) {
          onGenerationComplete();
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to start AI message generation');
        setGenerationStatus('failed');
      }
    } catch (error) {
      setError('Error starting AI message generation. Please try again.');
      setGenerationStatus('failed');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = () => {
    switch (generationStatus) {
      case 'completed':
        return <CheckIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'generating':
        return <AiIcon color="primary" />;
      default:
        return <AiIcon color="disabled" />;
    }
  };

  const getStatusColor = () => {
    switch (generationStatus) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'generating':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Stack spacing={3}>
          <Box display="flex" alignItems="center" gap={2}>
            <AiIcon color="primary" />
            <Typography variant="h6">
              AI Message Generation
            </Typography>
            <Chip
              label={`${totalWebsites} websites`}
              size="small"
              color="primary"
              variant="outlined"
            />
          </Box>

          <Typography variant="body2" color="text.secondary">
            Generate personalized AI messages for all websites in this file upload using Gemini AI.
            Messages will be customized based on the scraped company information.
          </Typography>

          <FormControl fullWidth>
            <InputLabel>Message Type</InputLabel>
            <Select
              value={messageType}
              label="Message Type"
              onChange={(e) => setMessageType(e.target.value)}
            >
              <MenuItem value="general">General Inquiry</MenuItem>
              <MenuItem value="partnership">Partnership Proposal</MenuItem>
              <MenuItem value="support">Support Request</MenuItem>
              <MenuItem value="custom">Custom</MenuItem>
            </Select>
          </FormControl>

          {messageType === 'custom' && (
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Custom Prompt"
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              helperText="Available variables: {company_name}, {industry}, {business_type}, {about_us_content}"
              placeholder="Enter your custom prompt for message generation..."
            />
          )}

          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">{success}</Alert>}

          {generationStatus === 'generating' && (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Generating AI messages...
              </Typography>
              <LinearProgress />
            </Box>
          )}

          <Box display="flex" alignItems="center" gap={2}>
            <Button
              variant="contained"
              onClick={handleGenerateMessages}
              disabled={loading || generationStatus === 'generating'}
              startIcon={loading ? <AiIcon /> : <PlayIcon />}
              size="large"
            >
              {loading ? 'Starting Generation...' : 'Generate AI Messages'}
            </Button>

            {generationStatus !== 'idle' && (
              <Chip
                icon={getStatusIcon()}
                label={generationStatus.charAt(0).toUpperCase() + generationStatus.slice(1)}
                color={getStatusColor()}
                variant="outlined"
              />
            )}
          </Box>

          <Typography variant="caption" color="text.secondary">
            💡 Tip: The AI will analyze each website's company information, industry, and business type to create highly personalized messages.
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
