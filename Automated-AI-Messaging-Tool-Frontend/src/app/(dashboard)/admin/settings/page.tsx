'use client';

import { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Card,
  CardContent,
  Stack,
  Alert,
  Divider,
  Chip,
  IconButton
} from '@mui/material';
import { Save, Settings, Security, Notifications, Storage, Speed, CheckCircle } from '@mui/icons-material';
import MainCard from '../../../../components/MainCard';

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState({
    // System Settings
    systemName: 'AI Messaging Tool',
    systemEmail: 'admin@aimessagingtool.com',
    maxFileSize: '5',
    maxWebsitesPerFile: '1000',
    enableRegistration: true,
    requireEmailVerification: true,

    // Security Settings
    enableTwoFactor: false,
    sessionTimeout: '30',
    maxLoginAttempts: '5',
    enableRateLimiting: true,

    // Notification Settings
    emailNotifications: true,
    systemAlerts: true,
    userActivityLogs: true,

    // Performance Settings
    enableCaching: true,
    cacheTimeout: '3600',
    enableCompression: true,
    maxConcurrentProcesses: '10'
  });

  const [saveSuccess, setSaveSuccess] = useState('');

  const handleSettingChange = (key: string, value: any) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSave = () => {
    // Mock save functionality
    console.log('Saving settings:', settings);
    setSaveSuccess('Settings saved successfully!');
    setTimeout(() => setSaveSuccess(''), 3000);
  };

  const settingSections = [
    {
      title: 'System Settings',
      icon: <Settings />,
      settings: [
        { key: 'systemName', label: 'System Name', type: 'text' },
        { key: 'systemEmail', label: 'System Email', type: 'text' },
        { key: 'maxFileSize', label: 'Max File Size (MB)', type: 'number' },
        { key: 'maxWebsitesPerFile', label: 'Max Websites per File', type: 'number' },
        { key: 'enableRegistration', label: 'Enable User Registration', type: 'switch' },
        { key: 'requireEmailVerification', label: 'Require Email Verification', type: 'switch' }
      ]
    },
    {
      title: 'Security Settings',
      icon: <Security />,
      settings: [
        { key: 'enableTwoFactor', label: 'Enable Two-Factor Authentication', type: 'switch' },
        { key: 'sessionTimeout', label: 'Session Timeout (minutes)', type: 'number' },
        { key: 'maxLoginAttempts', label: 'Max Login Attempts', type: 'number' },
        { key: 'enableRateLimiting', label: 'Enable Rate Limiting', type: 'switch' }
      ]
    },
    {
      title: 'Notification Settings',
      icon: <Notifications />,
      settings: [
        { key: 'emailNotifications', label: 'Email Notifications', type: 'switch' },
        { key: 'systemAlerts', label: 'System Alerts', type: 'switch' },
        { key: 'userActivityLogs', label: 'User Activity Logs', type: 'switch' }
      ]
    },
    {
      title: 'Performance Settings',
      icon: <Speed />,
      settings: [
        { key: 'enableCaching', label: 'Enable Caching', type: 'switch' },
        { key: 'cacheTimeout', label: 'Cache Timeout (seconds)', type: 'number' },
        { key: 'enableCompression', label: 'Enable Compression', type: 'switch' },
        { key: 'maxConcurrentProcesses', label: 'Max Concurrent Processes', type: 'number' }
      ]
    }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <MainCard sx={{ mb: 3, background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)', color: '#fff' }}>
        <Typography variant="h4" fontWeight={700} mb={1} sx={{ color: '#fff' }}>
          System Settings
        </Typography>
        <Typography variant="body1" sx={{ color: '#fff' }}>
          Configure system-wide settings and preferences
        </Typography>
      </MainCard>

      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }} icon={<CheckCircle />}>
          {saveSuccess}
        </Alert>
      )}

      <Grid container spacing={3}>
        {settingSections.map((section, sectionIndex) => (
          <Grid item xs={12} md={6} key={sectionIndex}>
            <MainCard title={section.title}>
              <Stack spacing={3}>
                {section.settings.map((setting, settingIndex) => (
                  <Box key={settingIndex}>
                    {setting.type === 'switch' ? (
                      <FormControlLabel
                        control={
                          <Switch
                            checked={settings[setting.key as keyof typeof settings] as boolean}
                            onChange={(e) => handleSettingChange(setting.key, e.target.checked)}
                            color="primary"
                          />
                        }
                        label={setting.label}
                      />
                    ) : (
                      <TextField
                        fullWidth
                        label={setting.label}
                        type={setting.type}
                        value={settings[setting.key as keyof typeof settings]}
                        onChange={(e) => handleSettingChange(setting.key, e.target.value)}
                        variant="outlined"
                      />
                    )}
                  </Box>
                ))}
              </Stack>
            </MainCard>
          </Grid>
        ))}
      </Grid>

      {/* Save Button */}
      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<Save />}
          onClick={handleSave}
          sx={{
            px: 4,
            py: 1.5,
            borderRadius: 2,
            fontWeight: 600
          }}
        >
          Save All Settings
        </Button>
      </Box>

      {/* System Status */}
      <MainCard title="System Status" sx={{ mt: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Chip label="Online" color="success" icon={<CheckCircle />} sx={{ mb: 1 }} />
              <Typography variant="subtitle2">System Status</Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h6" color="primary.main">
                99.9%
              </Typography>
              <Typography variant="subtitle2">Uptime</Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h6" color="success.main">
                2.3s
              </Typography>
              <Typography variant="subtitle2">Avg Response Time</Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h6" color="info.main">
                156
              </Typography>
              <Typography variant="subtitle2">Active Users</Typography>
            </Box>
          </Grid>
        </Grid>
      </MainCard>
    </Box>
  );
}
