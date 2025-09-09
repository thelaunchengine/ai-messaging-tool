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
import LinearProgress from '@mui/material/LinearProgress';
import CircularProgress from '@mui/material/CircularProgress';
import MainCard from '../../../../components/MainCard';
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
  AdminPanelSettings,
  People,
  Support,
  Analytics,
  Settings,
  Description,
  Timeline,
  Message
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  BarChart as RechartsBarChart,
  Bar
} from 'recharts';
import Container from '@mui/material/Container';

// Icon mapping for dynamic icons
const iconMap = {
  CloudUpload: <CloudUpload color="primary" />,
  ListAlt: <ListAlt color="secondary" />,
  CheckCircle: <CheckCircle color="success" />,
  Message: <Message color="info" />,
  ErrorOutline: <ErrorOutline color="error" />,
  People: <People color="warning" />,
  Assignment: <Assignment color="info" />
};

const recentUsers = [
  { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active', files: 12, lastActive: '2 hours ago' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'active', files: 8, lastActive: '1 day ago' },
  { id: 3, name: 'Mike Johnson', email: 'mike@example.com', status: 'disabled', files: 5, lastActive: '3 days ago' },
  { id: 4, name: 'Sarah Wilson', email: 'sarah@example.com', status: 'active', files: 15, lastActive: '5 hours ago' }
];

const systemActivity = [
  { type: 'File Upload', detail: 'websites_batch3.xlsx by user@example.com', time: '30 minutes ago' },
  { type: 'Message Sent', detail: 'Sent to 150 websites in Batch 3', time: '1 hour ago' },
  { type: 'User Registration', detail: 'New user: alex@example.com', time: '2 hours ago' },
  { type: 'File Upload', detail: 'websites_batch2.csv by user@example.com', time: '3 hours ago' },
  { type: 'Message Sent', detail: 'Sent to 200 websites in Batch 2', time: '4 hours ago' }
];

const quickActions = [
  { label: 'Users', icon: <People />, href: '/admin/users', color: 'primary' },
  { label: 'Support Chat', icon: <Support />, href: '/admin/support', color: 'secondary' },
  { label: 'Reports', icon: <Analytics />, href: '/admin/reports', color: 'success' },
  { label: 'Static Content', icon: <Description />, href: '/admin/content', color: 'info' },
  { label: 'File History', icon: <History />, href: '/admin/history', color: 'warning' },
  { label: 'System Settings', icon: <Settings />, href: '/admin/settings', color: 'error' }
];

const weeklyData = [
  { day: 'Mon', files: 12, websites: 150, messages: 120 },
  { day: 'Tue', files: 18, websites: 220, messages: 180 },
  { day: 'Wed', files: 15, websites: 180, messages: 150 },
  { day: 'Thu', files: 22, websites: 280, messages: 240 },
  { day: 'Fri', files: 25, websites: 320, messages: 280 },
  { day: 'Sat', files: 8, websites: 100, messages: 80 },
  { day: 'Sun', files: 5, websites: 60, messages: 50 }
];

export default function AdminDashboardPage() {
  const [adminStats, setAdminStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAdminStats = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/admin/dashboard/stats');
        
        if (!response.ok) {
          throw new Error('Failed to fetch admin dashboard statistics');
        }
        
        const data = await response.json();
        setAdminStats(data.stats);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchAdminStats();
  }, []);

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
        <Typography color="error" variant="h6">
          {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
          Admin Dashboard
        </Typography>
      </Box>

      {/* Admin Stats Section (metrics/stat boxes) */}
      <Grid container spacing={3} mb={3}>
        {adminStats.map((stat, idx) => (
          <Grid item xs={12} sm={6} md={4} key={idx}>
            <MainCard sx={{ p: 2, display: 'flex', alignItems: 'center', minHeight: 120 }}>
              <Box sx={{ mr: 2 }}>{iconMap[stat.icon as keyof typeof iconMap]}</Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  {stat.label}
                </Typography>
                <Typography variant="h5" fontWeight={700}>
                  {stat.value}
                </Typography>
                {/* Removed percentage chip */}
              </Box>
            </MainCard>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
