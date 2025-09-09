'use client';

import { useState } from 'react';
import {
  Box,
  Grid,
  Stack,
  Typography,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Paper
} from '@mui/material';
import MainCard from '../../../components/MainCard';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// Mock data - Replace with actual data from your backend
const messageStats = {
  total: 1250,
  successful: 980,
  failed: 270,
  pending: 0
};

const dailyStats = [
  { date: '2024-03-01', successful: 45, failed: 12 },
  { date: '2024-03-02', successful: 52, failed: 8 },
  { date: '2024-03-03', successful: 38, failed: 15 },
  { date: '2024-03-04', successful: 65, failed: 10 },
  { date: '2024-03-05', successful: 48, failed: 7 },
  { date: '2024-03-06', successful: 55, failed: 9 },
  { date: '2024-03-07', successful: 42, failed: 11 }
];

const successRateByIndustry = [
  { name: 'Technology', value: 85 },
  { name: 'Healthcare', value: 78 },
  { name: 'Finance', value: 82 },
  { name: 'Education', value: 75 },
  { name: 'Retail', value: 80 }
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('7d');
  const [chartType, setChartType] = useState('daily');

  const handleTimeRangeChange = (event: SelectChangeEvent) => {
    setTimeRange(event.target.value);
  };

  const handleChartTypeChange = (event: SelectChangeEvent) => {
    setChartType(event.target.value);
  };

  const successRate = ((messageStats.successful / messageStats.total) * 100).toFixed(1);

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h2">Analytics</Typography>
            <Stack direction="row" spacing={2}>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Time Range</InputLabel>
                <Select value={timeRange} label="Time Range" onChange={handleTimeRangeChange} size="small">
                  <MenuItem value="7d">Last 7 Days</MenuItem>
                  <MenuItem value="30d">Last 30 Days</MenuItem>
                  <MenuItem value="90d">Last 90 Days</MenuItem>
                  <MenuItem value="1y">Last Year</MenuItem>
                </Select>
              </FormControl>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Chart Type</InputLabel>
                <Select value={chartType} label="Chart Type" onChange={handleChartTypeChange} size="small">
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="weekly">Weekly</MenuItem>
                  <MenuItem value="monthly">Monthly</MenuItem>
                </Select>
              </FormControl>
            </Stack>
          </Stack>
        </Grid>

        {/* Summary Cards */}
        <Grid item xs={12} md={3}>
          <MainCard>
            <CardContent>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Total Messages
              </Typography>
              <Typography variant="h3">{messageStats.total}</Typography>
            </CardContent>
          </MainCard>
        </Grid>
        <Grid item xs={12} md={3}>
          <MainCard>
            <CardContent>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Successful
              </Typography>
              <Typography variant="h3" color="success.main">
                {messageStats.successful}
              </Typography>
            </CardContent>
          </MainCard>
        </Grid>
        <Grid item xs={12} md={3}>
          <MainCard>
            <CardContent>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Failed
              </Typography>
              <Typography variant="h3" color="error.main">
                {messageStats.failed}
              </Typography>
            </CardContent>
          </MainCard>
        </Grid>
        <Grid item xs={12} md={3}>
          <MainCard>
            <CardContent>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Success Rate
              </Typography>
              <Typography variant="h3" color="primary">
                {successRate}%
              </Typography>
            </CardContent>
          </MainCard>
        </Grid>

        {/* Daily Stats Chart */}
        <Grid item xs={12} md={8}>
          <MainCard title="Message Delivery Trends">
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dailyStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="successful" name="Successful" fill="#4CAF50" />
                  <Bar dataKey="failed" name="Failed" fill="#F44336" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </MainCard>
        </Grid>

        {/* Success Rate by Industry */}
        <Grid item xs={12} md={4}>
          <MainCard title="Success Rate by Industry">
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={successRateByIndustry}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {successRateByIndustry.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </MainCard>
        </Grid>

        {/* Additional Metrics */}
        <Grid item xs={12}>
          <MainCard title="Performance Metrics">
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={dailyStats}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="successful" name="Success Rate" stroke="#4CAF50" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Stack spacing={2}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Average Response Time
                    </Typography>
                    <Typography variant="h4">2.5 hours</Typography>
                  </Paper>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Peak Usage Hours
                    </Typography>
                    <Typography variant="body1">10:00 AM - 2:00 PM</Typography>
                  </Paper>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Most Active Days
                    </Typography>
                    <Typography variant="body1">Monday, Wednesday, Friday</Typography>
                  </Paper>
                </Stack>
              </Grid>
            </Grid>
          </MainCard>
        </Grid>
      </Grid>
    </Box>
  );
}
