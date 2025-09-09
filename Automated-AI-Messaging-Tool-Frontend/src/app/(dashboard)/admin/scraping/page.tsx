'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  Card,
  CardContent,
  Stack,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Settings,
  Visibility,
  Download,
  Delete,
  Pause,
  Timeline,
  Speed,
  Storage,
  BugReport
} from '@mui/icons-material';
import MainCard from '../../../../components/MainCard';

interface ScrapingJob {
  id: string;
  fileUploadId: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'PAUSED';
  totalWebsites: number;
  processedWebsites: number;
  failedWebsites: number;
  startedAt: string;
  completedAt?: string;
  errorMessage?: string;
  createdAt: string;
}

interface ScrapingConfig {
  maxConcurrentScrapes: number;
  requestDelay: number;
  timeout: number;
  retryAttempts: number;
  enableSelenium: boolean;
  enableProxy: boolean;
  userAgent: string;
}

const ScrapingManagementPage = () => {
  const [scrapingJobs, setScrapingJobs] = useState<ScrapingJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [configDialog, setConfigDialog] = useState(false);
  const [jobDetailsDialog, setJobDetailsDialog] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<ScrapingJob | null>(null);
  const [config, setConfig] = useState<ScrapingConfig>({
    maxConcurrentScrapes: 5,
    requestDelay: 2,
    timeout: 30,
    retryAttempts: 3,
    enableSelenium: true,
    enableProxy: false,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });

  useEffect(() => {
    fetchScrapingJobs();
    const interval = setInterval(fetchScrapingJobs, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchScrapingJobs = async () => {
    try {
      const response = await fetch('/api/scraping/jobs');
      if (response.ok) {
        const data = await response.json();
        setScrapingJobs(data.jobs || []);
      }
    } catch (error) {
      console.error('Error fetching scraping jobs:', error);
    }
  };

  const handleStartJob = async (jobId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/scraping/jobs/${jobId}/start`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchScrapingJobs();
      }
    } catch (error) {
      console.error('Error starting job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStopJob = async (jobId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/scraping/jobs/${jobId}/stop`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchScrapingJobs();
      }
    } catch (error) {
      console.error('Error stopping job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePauseJob = async (jobId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/scraping/jobs/${jobId}/pause`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchScrapingJobs();
      }
    } catch (error) {
      console.error('Error pausing job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResumeJob = async (jobId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/scraping/jobs/${jobId}/resume`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchScrapingJobs();
      }
    } catch (error) {
      console.error('Error resuming job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!confirm('Are you sure you want to delete this scraping job?')) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/scraping/jobs/${jobId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchScrapingJobs();
      }
    } catch (error) {
      console.error('Error deleting job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewJobDetails = async (jobId: string) => {
    try {
      const response = await fetch(`/api/scraping/jobs/${jobId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedJob(data.job);
        setJobDetailsDialog(jobId);
      }
    } catch (error) {
      console.error('Error fetching job details:', error);
    }
  };

  const handleSaveConfig = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/scraping/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      if (response.ok) {
        setConfigDialog(false);
      }
    } catch (error) {
      console.error('Error saving config:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'RUNNING':
        return 'primary';
      case 'FAILED':
        return 'error';
      case 'PAUSED':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getProgressPercentage = (job: ScrapingJob) => {
    if (job.totalWebsites === 0) return 0;
    return Math.round((job.processedWebsites / job.totalWebsites) * 100);
  };

  const getActiveJobs = () => scrapingJobs.filter((job) => job.status === 'RUNNING' || job.status === 'PENDING');
  const getCompletedJobs = () => scrapingJobs.filter((job) => job.status === 'COMPLETED');
  const getFailedJobs = () => scrapingJobs.filter((job) => job.status === 'FAILED');

  return (
    <Box sx={{ p: 3 }}>
      <MainCard sx={{ mb: 3, background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)', color: '#fff' }}>
        <Grid container alignItems="center" spacing={2}>
          <Grid item xs={12} md={8}>
            <Typography variant="h4" fontWeight={700} mb={1} sx={{ color: '#fff' }}>
              Scraping Management
            </Typography>
            <Typography variant="body1" sx={{ color: '#fff' }}>
              Monitor and control website scraping jobs, manage configurations, and track progress
            </Typography>
          </Grid>
          <Grid item xs={12} md={4} sx={{ textAlign: 'right' }}>
            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                startIcon={<Settings />}
                onClick={() => setConfigDialog(true)}
                sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } }}
              >
                Configuration
              </Button>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={fetchScrapingJobs}
                disabled={loading}
                sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } }}
              >
                Refresh
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </MainCard>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MainCard>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="primary" gutterBottom>
                {getActiveJobs().length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Jobs
              </Typography>
            </CardContent>
          </MainCard>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MainCard>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="success.main" gutterBottom>
                {getCompletedJobs().length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed Jobs
              </Typography>
            </CardContent>
          </MainCard>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MainCard>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="error.main" gutterBottom>
                {getFailedJobs().length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Failed Jobs
              </Typography>
            </CardContent>
          </MainCard>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MainCard>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="info.main" gutterBottom>
                {scrapingJobs.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Jobs
              </Typography>
            </CardContent>
          </MainCard>
        </Grid>
      </Grid>

      {/* Scraping Jobs Table */}
      <MainCard title="Scraping Jobs">
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Job ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Websites</TableCell>
                <TableCell>Started</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {scrapingJobs.map((job) => (
                <TableRow key={job.id}>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {job.id.substring(0, 8)}...
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={job.status} color={getStatusColor(job.status) as any} size="small" />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ width: '100%' }}>
                      <LinearProgress variant="determinate" value={getProgressPercentage(job)} sx={{ height: 8, borderRadius: 4 }} />
                      <Typography variant="caption" color="text.secondary">
                        {job.processedWebsites}/{job.totalWebsites} ({getProgressPercentage(job)}%)
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      <Typography variant="body2">Total: {job.totalWebsites}</Typography>
                      <Typography variant="body2" color="success.main">
                        ✓ {job.processedWebsites}
                      </Typography>
                      <Typography variant="body2" color="error.main">
                        ✗ {job.failedWebsites}
                      </Typography>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{new Date(job.startedAt || job.createdAt).toLocaleString()}</Typography>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => handleViewJobDetails(job.id)}>
                          <Visibility />
                        </IconButton>
                      </Tooltip>

                      {job.status === 'PENDING' && (
                        <Tooltip title="Start Job">
                          <IconButton size="small" color="primary" onClick={() => handleStartJob(job.id)} disabled={loading}>
                            <PlayArrow />
                          </IconButton>
                        </Tooltip>
                      )}

                      {job.status === 'RUNNING' && (
                        <>
                          <Tooltip title="Pause Job">
                            <IconButton size="small" color="warning" onClick={() => handlePauseJob(job.id)} disabled={loading}>
                              <Pause />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Stop Job">
                            <IconButton size="small" color="error" onClick={() => handleStopJob(job.id)} disabled={loading}>
                              <Stop />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}

                      {job.status === 'PAUSED' && (
                        <Tooltip title="Resume Job">
                          <IconButton size="small" color="primary" onClick={() => handleResumeJob(job.id)} disabled={loading}>
                            <PlayArrow />
                          </IconButton>
                        </Tooltip>
                      )}

                      <Tooltip title="Delete Job">
                        <IconButton size="small" color="error" onClick={() => handleDeleteJob(job.id)} disabled={loading}>
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </MainCard>

      {/* Configuration Dialog */}
      <Dialog open={configDialog} onClose={() => setConfigDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Scraping Configuration</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Max Concurrent Scrapes"
                type="number"
                value={config.maxConcurrentScrapes}
                onChange={(e) => setConfig({ ...config, maxConcurrentScrapes: parseInt(e.target.value) })}
                helperText="Maximum number of websites to scrape simultaneously"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Request Delay (seconds)"
                type="number"
                value={config.requestDelay}
                onChange={(e) => setConfig({ ...config, requestDelay: parseInt(e.target.value) })}
                helperText="Delay between requests to be respectful to websites"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Timeout (seconds)"
                type="number"
                value={config.timeout}
                onChange={(e) => setConfig({ ...config, timeout: parseInt(e.target.value) })}
                helperText="Request timeout for each website"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Retry Attempts"
                type="number"
                value={config.retryAttempts}
                onChange={(e) => setConfig({ ...config, retryAttempts: parseInt(e.target.value) })}
                helperText="Number of retry attempts for failed requests"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="User Agent"
                value={config.userAgent}
                onChange={(e) => setConfig({ ...config, userAgent: e.target.value })}
                helperText="User agent string for requests"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch checked={config.enableSelenium} onChange={(e) => setConfig({ ...config, enableSelenium: e.target.checked })} />
                }
                label="Enable Selenium for JavaScript-heavy sites"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={<Switch checked={config.enableProxy} onChange={(e) => setConfig({ ...config, enableProxy: e.target.checked })} />}
                label="Enable Proxy Support"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveConfig} variant="contained" disabled={loading}>
            Save Configuration
          </Button>
        </DialogActions>
      </Dialog>

      {/* Job Details Dialog */}
      <Dialog open={!!jobDetailsDialog} onClose={() => setJobDetailsDialog(null)} maxWidth="md" fullWidth>
        <DialogTitle>Job Details</DialogTitle>
        <DialogContent>
          {selectedJob && (
            <Stack spacing={3} sx={{ mt: 1 }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Job ID
                  </Typography>
                  <Typography variant="body1" fontFamily="monospace">
                    {selectedJob.id}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip label={selectedJob.status} color={getStatusColor(selectedJob.status) as any} />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Total Websites
                  </Typography>
                  <Typography variant="body1">{selectedJob.totalWebsites}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Processed
                  </Typography>
                  <Typography variant="body1" color="success.main">
                    {selectedJob.processedWebsites}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Failed
                  </Typography>
                  <Typography variant="body1" color="error.main">
                    {selectedJob.failedWebsites}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Created
                  </Typography>
                  <Typography variant="body1">{new Date(selectedJob.createdAt).toLocaleString()}</Typography>
                </Grid>
                {selectedJob.startedAt && (
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Started
                    </Typography>
                    <Typography variant="body1">{new Date(selectedJob.startedAt).toLocaleString()}</Typography>
                  </Grid>
                )}
                {selectedJob.completedAt && (
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Completed
                    </Typography>
                    <Typography variant="body1">{new Date(selectedJob.completedAt).toLocaleString()}</Typography>
                  </Grid>
                )}
              </Grid>

              {selectedJob.errorMessage && (
                <Alert severity="error">
                  <Typography variant="subtitle2">Error Message</Typography>
                  <Typography variant="body2">{selectedJob.errorMessage}</Typography>
                </Alert>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setJobDetailsDialog(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ScrapingManagementPage;
