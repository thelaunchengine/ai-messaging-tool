'use client';

import { useState } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import Divider from '@mui/material/Divider';
import Alert from '@mui/material/Alert';

// project-imports
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

// ==============================|| SETTINGS ||============================== //

export default function Settings() {
  const theme = useTheme();
  const [settings, setSettings] = useState({
    aiModel: 'gpt-4',
    apiKey: '',
    maxRetries: 3,
    delayBetweenRequests: 5,
    autoSave: true,
    notifications: true,
    defaultMessageType: 'general',
    customPrompt: ''
  });

  const handleChange = (field: string) => (event: any) => {
    setSettings({
      ...settings,
      [field]: event.target.value
    });
  };

  const handleSwitchChange = (field: string) => (event: any) => {
    setSettings({
      ...settings,
      [field]: event.target.checked
    });
  };

  return (
    <Grid container spacing={GRID_COMMON_SPACING}>
      <Grid size={12}>
        <MainCard title="AI Model Settings">
          <Stack spacing={3}>
            <FormControl fullWidth>
              <InputLabel>AI Model</InputLabel>
              <Select value={settings.aiModel} label="AI Model" onChange={handleChange('aiModel')}>
                <MenuItem value="gpt-4">GPT-4</MenuItem>
                <MenuItem value="gpt-3.5">GPT-3.5</MenuItem>
                <MenuItem value="gemini">Gemini</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="API Key"
              type="password"
              value={settings.apiKey}
              onChange={handleChange('apiKey')}
              helperText="Enter your API key for the selected AI model"
            />

            <TextField
              fullWidth
              label="Max Retries"
              type="number"
              value={settings.maxRetries}
              onChange={handleChange('maxRetries')}
              helperText="Maximum number of retry attempts for failed requests"
            />

            <TextField
              fullWidth
              label="Delay Between Requests (seconds)"
              type="number"
              value={settings.delayBetweenRequests}
              onChange={handleChange('delayBetweenRequests')}
              helperText="Time to wait between processing each website"
            />
          </Stack>
        </MainCard>
      </Grid>

      <Grid size={12}>
        <MainCard title="Automation Preferences">
          <Stack spacing={3}>
            <FormControlLabel
              control={<Switch checked={settings.autoSave} onChange={handleSwitchChange('autoSave')} />}
              label="Auto-save Results"
            />

            <FormControlLabel
              control={<Switch checked={settings.notifications} onChange={handleSwitchChange('notifications')} />}
              label="Enable Notifications"
            />

            <FormControl fullWidth>
              <InputLabel>Default Message Type</InputLabel>
              <Select value={settings.defaultMessageType} label="Default Message Type" onChange={handleChange('defaultMessageType')}>
                <MenuItem value="general">General Inquiry</MenuItem>
                <MenuItem value="partnership">Partnership Proposal</MenuItem>
                <MenuItem value="support">Support Request</MenuItem>
                <MenuItem value="custom">Custom</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Custom Prompt Template"
              multiline
              rows={4}
              value={settings.customPrompt}
              onChange={handleChange('customPrompt')}
              helperText="Enter your custom prompt template. Use {website}, {business_type}, {company_name}, {industry} as variables."
            />
          </Stack>
        </MainCard>
      </Grid>

      <Grid size={12}>
        <Alert severity="info">
          Changes will be applied immediately. Make sure to test your settings with a small batch of websites first.
        </Alert>
      </Grid>

      <Grid size={12}>
        <Stack direction="row" spacing={2} justifyContent="flex-end">
          <Button variant="outlined" color="secondary">
            Reset to Default
          </Button>
          <Button variant="contained" color="primary">
            Save Settings
          </Button>
        </Stack>
      </Grid>
    </Grid>
  );
}
