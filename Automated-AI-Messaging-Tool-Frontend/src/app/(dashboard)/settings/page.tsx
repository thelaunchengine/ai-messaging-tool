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
  Switch,
  FormControlLabel,
  Alert,
  SelectChangeEvent
} from '@mui/material';
import { useTheme } from '@mui/material';
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

export default function Settings() {
  const theme = useTheme();
  const [settings, setSettings] = useState({
    apiKey: '',
    defaultAiModel: 'gpt-4',
    maxRetries: 3,
    delayBetweenMessages: 5,
    notifications: true,
    autoSave: true
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setSettings((prev) => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSelectChange = (field: string) => (event: SelectChangeEvent) => {
    setSettings((prev) => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSwitchChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setSettings((prev) => ({
      ...prev,
      [field]: event.target.checked
    }));
  };

  const handleSave = () => {
    if (!settings.apiKey) {
      setError('API key is required');
      return;
    }
    // TODO: Implement save logic
    console.log('Saving settings:', settings);
    setSuccess('Settings saved successfully');
    setError('');
  };

  return (
    <Grid container spacing={GRID_COMMON_SPACING}>
      <Grid xs={12}>
        <Typography variant="h3">Settings</Typography>
      </Grid>

      <Grid xs={12} md={6}>
        <MainCard title="API Configuration">
          <Stack spacing={3}>
            <TextField
              fullWidth
              label="API Key"
              type="password"
              value={settings.apiKey}
              onChange={handleInputChange('apiKey')}
              error={!!error}
              helperText={error}
            />

            <FormControl fullWidth>
              <InputLabel>Default AI Model</InputLabel>
              <Select value={settings.defaultAiModel} label="Default AI Model" onChange={handleSelectChange('defaultAiModel')}>
                <MenuItem value="gpt-4">GPT-4</MenuItem>
                <MenuItem value="gpt-3.5">GPT-3.5</MenuItem>
                <MenuItem value="gemini">Gemini</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              type="number"
              label="Max Retries"
              value={settings.maxRetries}
              onChange={handleInputChange('maxRetries')}
              inputProps={{ min: 1, max: 10 }}
            />

            <TextField
              fullWidth
              type="number"
              label="Delay Between Messages (seconds)"
              value={settings.delayBetweenMessages}
              onChange={handleInputChange('delayBetweenMessages')}
              inputProps={{ min: 1, max: 60 }}
            />
          </Stack>
        </MainCard>
      </Grid>

      <Grid xs={12} md={6}>
        <MainCard title="Preferences">
          <Stack spacing={3}>
            <FormControlLabel
              control={<Switch checked={settings.notifications} onChange={handleSwitchChange('notifications')} />}
              label="Enable Notifications"
            />

            <FormControlLabel
              control={<Switch checked={settings.autoSave} onChange={handleSwitchChange('autoSave')} />}
              label="Auto-save Changes"
            />
          </Stack>
        </MainCard>
      </Grid>

      <Grid xs={12}>
        <Stack direction="row" spacing={2} justifyContent="flex-end">
          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">{success}</Alert>}
          <Button variant="contained" onClick={handleSave}>
            Save Settings
          </Button>
        </Stack>
      </Grid>
    </Grid>
  );
}
