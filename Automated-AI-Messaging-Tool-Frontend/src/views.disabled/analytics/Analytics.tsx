'use client';

import { useState } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';

// project-imports
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

// assets
import { DocumentDownload, Calendar } from '@wandersonalwes/iconsax-react';

// ==============================|| ANALYTICS ||============================== //

export default function Analytics() {
  const theme = useTheme();
  const [timeRange, setTimeRange] = useState('7d');

  // Mock data for charts and tables
  const stats = {
    totalWebsites: 150,
    successfulMessages: 98,
    failedMessages: 12,
    pendingMessages: 40,
    averageResponseTime: '2.5s',
    successRate: '89%'
  };

  const messageTypes = [
    { type: 'General Inquiry', count: 45, successRate: '92%' },
    { type: 'Partnership Proposal', count: 35, successRate: '85%' },
    { type: 'Support Request', count: 30, successRate: '95%' },
    { type: 'Custom', count: 40, successRate: '88%' }
  ];

  const recentActivity = [
    {
      website: 'example1.com',
      type: 'General Inquiry',
      status: 'Success',
      timestamp: '2024-03-20 10:30:45'
    },
    {
      website: 'example2.com',
      type: 'Partnership Proposal',
      status: 'Failed',
      timestamp: '2024-03-20 10:31:12'
    },
    {
      website: 'example3.com',
      type: 'Support Request',
      status: 'Success',
      timestamp: '2024-03-20 10:31:45'
    }
  ];

  return (
    <Grid container spacing={GRID_COMMON_SPACING}>
      <Grid size={12}>
        <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
          <Typography variant="h3">Analytics Dashboard</Typography>
          <Stack direction="row" spacing={2}>
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel>Time Range</InputLabel>
              <Select value={timeRange} label="Time Range" onChange={(e) => setTimeRange(e.target.value)} startAdornment={<Calendar />}>
                <MenuItem value="24h">Last 24 Hours</MenuItem>
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
                <MenuItem value="90d">Last 90 Days</MenuItem>
              </Select>
            </FormControl>
            <Button variant="outlined" color="primary" startIcon={<DocumentDownload />}>
              Export Report
            </Button>
          </Stack>
        </Stack>
      </Grid>

      <Grid size={12}>
        <Grid container spacing={2}>
          <Grid size={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={1}>
                <Typography variant="subtitle2" color="textSecondary">
                  Total Websites
                </Typography>
                <Typography variant="h4">{stats.totalWebsites}</Typography>
              </Stack>
            </Paper>
          </Grid>
          <Grid size={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={1}>
                <Typography variant="subtitle2" color="textSecondary">
                  Success Rate
                </Typography>
                <Typography variant="h4">{stats.successRate}</Typography>
              </Stack>
            </Paper>
          </Grid>
          <Grid size={12} md={4}>
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={1}>
                <Typography variant="subtitle2" color="textSecondary">
                  Avg. Response Time
                </Typography>
                <Typography variant="h4">{stats.averageResponseTime}</Typography>
              </Stack>
            </Paper>
          </Grid>
        </Grid>
      </Grid>

      <Grid size={12} md={6}>
        <MainCard title="Message Types">
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Count</TableCell>
                  <TableCell align="right">Success Rate</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {messageTypes.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.type}</TableCell>
                    <TableCell align="right">{row.count}</TableCell>
                    <TableCell align="right">{row.successRate}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </MainCard>
      </Grid>

      <Grid size={12} md={6}>
        <MainCard title="Recent Activity">
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Website</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Timestamp</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentActivity.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.website}</TableCell>
                    <TableCell>{row.type}</TableCell>
                    <TableCell>{row.status}</TableCell>
                    <TableCell>{row.timestamp}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </MainCard>
      </Grid>
    </Grid>
  );
}
