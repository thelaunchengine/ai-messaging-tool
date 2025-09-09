'use client';
import SafeLinearProgress from './SafeLinearProgress';

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  
  Chip,
  Stack,
  IconButton,
  Collapse,
  Alert
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Pending,
  ExpandMore,
  ExpandLess,
  Refresh
} from '@mui/icons-material';
import websocketManager from '../lib/websocket';

interface ProgressData {
  current: number;
  total: number;
  progress: number;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  message?: string;
  error?: string;
}

interface RealTimeProgressProps {
  taskId?: string;
  fileUploadId?: string;
  jobId?: string;
  title: string;
  onComplete?: (data: ProgressData) => void;
  onError?: (error: string) => void;
}

export default function RealTimeProgress({
  taskId,
  fileUploadId,
  jobId,
  title,
  onComplete,
  onError
}: RealTimeProgressProps) {
  const [progressData, setProgressData] = useState<ProgressData>({
    current: 0,
    total: 0,
    progress: 0,
    status: 'PENDING'
  });
  const [expanded, setExpanded] = useState(true);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Check WebSocket connection
    setIsConnected(websocketManager.isConnected());

    // Subscribe to appropriate updates based on provided IDs
    if (taskId) {
      websocketManager.subscribeToTaskProgress(taskId, handleProgressUpdate);
    }
    if (fileUploadId) {
      websocketManager.subscribeToFileUploadProgress(fileUploadId, handleProgressUpdate);
    }
    if (jobId) {
      websocketManager.subscribeToScrapingJob(jobId, handleProgressUpdate);
    }

    return () => {
      // Cleanup subscriptions
      if (taskId) {
        websocketManager.unsubscribe(`task_progress_${taskId}`);
      }
      if (fileUploadId) {
        websocketManager.unsubscribe(`file_upload_progress_${fileUploadId}`);
      }
      if (jobId) {
        websocketManager.unsubscribe(`scraping_job_update_${jobId}`);
      }
    };
  }, [taskId, fileUploadId, jobId]);

  const handleProgressUpdate = (data: ProgressData) => {
    setProgressData(data);
    
    if (data.status === 'COMPLETED' && onComplete) {
      onComplete(data);
    }
    
    if (data.status === 'FAILED' && onError) {
      onError(data.error || 'Task failed');
    }
  };

  const getStatusIcon = () => {
    switch (progressData.status) {
      case 'COMPLETED':
        return <CheckCircle color="success" />;
      case 'FAILED':
        return <Error color="error" />;
      case 'PROCESSING':
        return <Refresh color="primary" />;
      default:
        return <Pending color="warning" />;
    }
  };

  const getStatusColor = () => {
    switch (progressData.status) {
      case 'COMPLETED':
        return 'success';
      case 'FAILED':
        return 'error';
      case 'PROCESSING':
        return 'primary';
      default:
        return 'warning';
    }
  };

  const getStatusText = () => {
    switch (progressData.status) {
      case 'COMPLETED':
        return 'Completed';
      case 'FAILED':
        return 'Failed';
      case 'PROCESSING':
        return 'Processing';
      default:
        return 'Pending';
    }
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Stack direction="row" spacing={1} alignItems="center">
            {getStatusIcon()}
            <Typography variant="h6">{title}</Typography>
            <Chip
              label={getStatusText()}
              color={getStatusColor() as any}
              size="small"
            />
            {!isConnected && (
              <Chip
                label="Offline"
                color="error"
                size="small"
                variant="outlined"
              />
            )}
          </Stack>
          <Stack direction="row" spacing={1}>
            <IconButton
              size="small"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Stack>
        </Stack>

        <Collapse in={expanded}>
          <Box>
            <Stack direction="row" justifyContent="space-between" mb={1}>
              <Typography variant="body2" color="text.secondary">
                Progress: {progressData.current} / {progressData.total}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {progressData.progress}%
              </Typography>
            </Stack>
            
            <SafeLinearProgress
              variant="determinate"
              value={progressData.progress}
              sx={{ mb: 2 }}
            />

            {progressData.message && (
              <Alert severity="info" sx={{ mb: 1 }}>
                {progressData.message}
              </Alert>
            )}

            {progressData.error && (
              <Alert severity="error" sx={{ mb: 1 }}>
                {progressData.error}
              </Alert>
            )}

            {progressData.total > 0 && (
              <Typography variant="caption" color="text.secondary">
                {progressData.current} of {progressData.total} items processed
              </Typography>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
} 