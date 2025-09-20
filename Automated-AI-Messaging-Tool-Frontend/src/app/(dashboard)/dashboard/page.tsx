'use client';

import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Avatar from '@mui/material/Avatar';
import Divider from '@mui/material/Divider';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import MainCard from '../../../components/MainCard';
import {
  TrendingUp,
  BarChart,
  TaskAlt,
  CloudDownload,
  RocketLaunch,
  Group,
  Assignment,
  PieChart as PieChartIcon,
  CloudUpload,
  History,
  Assessment,
  HelpOutline,
  CheckCircle,
  ErrorOutline,
  ListAlt,
  Message,
  Web,
  BatchPrediction
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { normalizeStatus } from '../../../utils/statusUtils';

// Icon mapping for dynamic icons
const iconMap = {
  CloudUpload: <CloudUpload color="primary" />,
  ListAlt: <ListAlt color="secondary" />,
  CheckCircle: <CheckCircle color="success" />,
  Message: <Message color="info" />,
  ErrorOutline: <ErrorOutline color="error" />,
  BatchPrediction: <BatchPrediction color="warning" />
};

const quickLinks = [
  { label: 'List', icon: <CloudUpload />, href: '/list-name', color: 'primary' },
  { label: 'History', icon: <History />, href: '/history', color: 'secondary' }
];

interface DashboardStats {
  firstRow: Array<{
    label: string;
    value: number | string;
    icon: string;
  }>;
  secondRow: Array<{
    label: string;
    value: number | string;
    icon: string;
  }>;
  recentActivity: Array<{
    type: string;
    detail: string;
    time: string;
    status?: string;
    websites?: number;
  }>;
}

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Get user from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  useEffect(() => {
    const fetchStats = async () => {
      if (!user) return;
      
      try {
        setLoading(true);
        const response = await fetch(`/api/dashboard/stats?userId=${user.id}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch dashboard statistics');
        }
        
        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [user]);

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!stats) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          No dashboard data available
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
          Welcome, {user?.name || 'User'}! AI Messaging Tool Dashboard
        </Typography>
      </Box>

      {/* Stats - 6 Compact Boxes in 2 Rows of 3 Columns */}
      <Grid container spacing={3} mb={3} alignItems="stretch">
        {stats.firstRow.map((stat, idx) => (
          <Grid item xs={12} sm={6} md={4} key={idx}>
            <MainCard sx={{
              height: 160,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              p: 3,
              borderRadius: 2,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              transition: 'all 0.3s ease',
              '&:hover': {
                boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
                transform: 'translateY(-2px)'
              }
            }}>
              <Box sx={{ 
                mb: 2, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                fontSize: 40,
                color: 'primary.main'
              }}>
                {iconMap[stat.icon as keyof typeof iconMap]}
              </Box>
              <Typography 
                variant="subtitle2" 
                color="text.secondary" 
                mb={1} 
                align="center"
                sx={{ fontWeight: 500, fontSize: '0.875rem' }}
              >
                {stat.label}
              </Typography>
              <Typography 
                variant="h4" 
                fontWeight={700} 
                align="center" 
                sx={{ 
                  fontSize: '1.25rem !important',
                  color: 'text.primary',
                  lineHeight: 1.2
                }}
              >
                {stat.value}
              </Typography>
            </MainCard>
          </Grid>
        ))}
      </Grid>
      <Grid container spacing={3} mb={3} alignItems="stretch">
        {stats.secondRow.map((stat, idx) => (
          <Grid item xs={12} sm={6} md={4} key={idx}>
            <MainCard sx={{
              height: 160,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              p: 3,
              borderRadius: 2,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              transition: 'all 0.3s ease',
              '&:hover': {
                boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
                transform: 'translateY(-2px)'
              }
            }}>
              <Box sx={{ 
                mb: 2, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                fontSize: 40,
                color: 'primary.main'
              }}>
                {iconMap[stat.icon as keyof typeof iconMap]}
              </Box>
              <Typography 
                variant="subtitle2" 
                color="text.secondary" 
                mb={1} 
                align="center"
                sx={{ fontWeight: 500, fontSize: '0.875rem' }}
              >
                {stat.label}
              </Typography>
              <Typography 
                variant="h4" 
                fontWeight={700} 
                align="center" 
                sx={{ 
                  fontSize: '1.25rem !important',
                  color: 'text.primary',
                  lineHeight: 1.2
                }}
              >
                {stat.value}
              </Typography>
            </MainCard>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Activity */}
        <Grid item xs={12} md={8}>
          <MainCard sx={{ p: 3 }}>
            <Typography variant="subtitle1" mb={2}>
              Recent Activity
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Stack spacing={2}>
              {stats.recentActivity.length > 0 ? (
                stats.recentActivity.map((activity, idx) => (
                  <Stack key={idx} direction="row" alignItems="center" spacing={2}>
                    <Typography variant="body2" fontWeight={600}>
                      {activity.type}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {activity.detail}
                      {activity.websites && ` (${activity.websites} websites)`}
                    </Typography>
                    <Chip 
                      label={normalizeStatus(activity.status || 'Unknown').label} 
                      size="small" 
                      color={normalizeStatus(activity.status || 'Unknown').color}
                      sx={{ ml: 'auto' }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {activity.time}
                    </Typography>
                  </Stack>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary" align="center">
                  No recent activity
                </Typography>
              )}
            </Stack>
          </MainCard>
        </Grid>

        {/* Quick Links */}
        <Grid item xs={12} md={4}>
          <MainCard sx={{ p: 3 }}>
            <Typography variant="subtitle1" mb={2}>
              Quick Links
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Stack spacing={2}>
              {quickLinks.map((link, idx) => (
                <Button
                  key={idx}
                  variant="contained"
                  color={link.color}
                  href={link.href}
                  startIcon={link.icon}
                  sx={{ borderRadius: 8, fontWeight: 600 }}
                  fullWidth
                >
                  {link.label}
                </Button>
              ))}
            </Stack>
          </MainCard>
        </Grid>
      </Grid>
    </Box>
  );
}
