'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  Stack,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Button
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Refresh,
  TrendingUp,
  TrendingDown,
  Speed,
  Memory,
  Storage,
  NetworkCheck
} from '@mui/icons-material';
import MainCard from '../../../components/MainCard';
import RealTimeProgress from '../../../components/RealTimeProgress';
import DetailedActivityView from '../../../components/DetailedActivityView';
import websocketManager from '../../../lib/websocket';

interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  activeTasks: number;
  queueSize: number;
  errorRate: number;
  successRate: number;
}

interface TaskMetrics {
  id: string;
  type: string;
  status: string;
  progress: number;
  startTime: string;
  duration: string;
  errorCount: number;
}

export default function MonitoringPage() {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
    activeTasks: 0,
    queueSize: 0,
    errorRate: 0,
    successRate: 0
  });
  const [taskMetrics, setTaskMetrics] = useState<TaskMetrics[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSystemMetrics();

    // Check WebSocket connection
    setIsConnected(websocketManager.isConnected());
  }, []);

  const fetchSystemMetrics = async () => {
    try {
      const response = await fetch('/api/monitoring/system-metrics');
      if (response.ok) {
        const data = await response.json();
        setSystemMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
      setError('Failed to fetch system metrics');
    } finally {
      setLoading(false);
    }
  };

  const fetchTaskMetrics = async () => {
    try {
      const response = await fetch('/api/monitoring/task-metrics');
      if (response.ok) {
        const data = await response.json();
        setTaskMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch task metrics:', error);
    }
  };

  const getHealthStatus = () => {
    if (systemMetrics.errorRate > 10) return 'error';
    if (systemMetrics.errorRate > 5) return 'warning';
    return 'success';
  };

  const getHealthIcon = () => {
    switch (getHealthStatus()) {
      case 'error':
        return <Error color="error" />;
      case 'warning':
        return <Warning color="warning" />;
      default:
        return <CheckCircle color="success" />;
    }
  };

  const getHealthText = () => {
    switch (getHealthStatus()) {
      case 'error':
        return 'Critical';
      case 'warning':
        return 'Warning';
      default:
        return 'Healthy';
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="h6" mt={2}>Loading system metrics...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">System Monitoring</Typography>
        <Stack direction="row" spacing={2}>
          <Chip
            icon={getHealthIcon()}
            label={getHealthText()}
            color={getHealthStatus() as any}
            variant="outlined"
          />
          {!isConnected && (
            <Chip
              label="WebSocket Offline"
              color="error"
              variant="outlined"
            />
          )}
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchSystemMetrics}
          >
            Refresh
          </Button>
        </Stack>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* System Health Overview */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <MainCard>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Speed color="primary" />
                <Box>
                  <Typography variant="h6">{systemMetrics.cpu}%</Typography>
                  <Typography variant="body2" color="text.secondary">CPU Usage</Typography>
                </Box>
              </Stack>
            </CardContent>
          </MainCard>
        </Grid>

        <Grid item xs={12} md={3}>
          <MainCard>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Memory color="primary" />
                <Box>
                  <Typography variant="h6">{systemMetrics.memory}%</Typography>
                  <Typography variant="body2" color="text.secondary">Memory Usage</Typography>
                </Box>
              </Stack>
            </CardContent>
          </MainCard>
        </Grid>

        <Grid item xs={12} md={3}>
          <MainCard>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Storage color="primary" />
                <Box>
                  <Typography variant="h6">{systemMetrics.disk}%</Typography>
                  <Typography variant="body2" color="text.secondary">Disk Usage</Typography>
                </Box>
              </Stack>
            </CardContent>
          </MainCard>
        </Grid>

        <Grid item xs={12} md={3}>
          <MainCard>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <NetworkCheck color="primary" />
                <Box>
                  <Typography variant="h6">{systemMetrics.network}%</Typography>
                  <Typography variant="body2" color="text.secondary">Network</Typography>
                </Box>
              </Stack>
            </CardContent>
          </MainCard>
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <MainCard title="Task Queue">
            <CardContent>
              <Stack spacing={2}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2">Active Tasks</Typography>
                  <Typography variant="h6">{systemMetrics.activeTasks}</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2">Queue Size</Typography>
                  <Typography variant="h6">{systemMetrics.queueSize}</Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2">Success Rate</Typography>
                  <Typography variant="h6" color="success.main">
                    {systemMetrics.successRate}%
                  </Typography>
                </Stack>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="body2">Error Rate</Typography>
                  <Typography variant="h6" color="error.main">
                    {systemMetrics.errorRate}%
                  </Typography>
                </Stack>
              </Stack>
            </CardContent>
          </MainCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <MainCard title="Performance Trends">
            <CardContent>
              <Stack spacing={2}>
                <Box>
                  <Stack direction="row" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">Success Rate Trend</Typography>
                    <TrendingUp color="success" />
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={systemMetrics.successRate}
                    color="success"
                  />
                </Box>
                <Box>
                  <Stack direction="row" justifyContent="space-between" mb={1}>
                    <Typography variant="body2">Error Rate Trend</Typography>
                    <TrendingDown color="error" />
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={systemMetrics.errorRate}
                    color="error"
                  />
                </Box>
              </Stack>
            </CardContent>
          </MainCard>
        </Grid>
      </Grid>

      {/* Active Tasks */}
      <MainCard title="Active Tasks">
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Task ID</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Errors</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {taskMetrics.map((task) => (
                <TableRow key={task.id}>
                  <TableCell>{task.id}</TableCell>
                  <TableCell>{task.type}</TableCell>
                  <TableCell>
                    <Chip
                      label={task.status}
                      color={task.status === 'COMPLETED' ? 'success' : 
                             task.status === 'FAILED' ? 'error' : 'warning'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={task.progress}
                        />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="text.secondary">
                          {task.progress}%
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>{task.duration}</TableCell>
                  <TableCell>
                    {task.errorCount > 0 ? (
                      <Chip
                        label={task.errorCount}
                        color="error"
                        size="small"
                      />
                    ) : (
                      <Chip
                        label="0"
                        color="success"
                        size="small"
                      />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </MainCard>

      {/* Detailed Activity Tracking */}
      <Box sx={{ mt: 4 }}>
        <DetailedActivityView />
      </Box>
    </Box>
  );
} 