'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Pending as PendingIcon,
  Error as ErrorIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import WebsiteDetailsView from './WebsiteDetailsView';

interface ActivityDetail {
  website?: string;
  status?: string;
  data_collected?: {
    title?: string;
    company_name?: string;
    industry?: string;
    contact_form?: string;
    about_us?: string;
  };
}

interface Activity {
  step: number;
  name: string;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'PENDING' | 'FAILED';
  description: string;
  timestamp: string;
  details: {
    file_size?: string;
    file_type?: string;
    total_rows?: number;
    validation?: string;
    data_extraction?: string;
    total_websites?: number;
    processed?: number;
    failed?: number;
    sample_websites?: ActivityDetail[];
    ai_model?: string;
    message_type?: string;
    generation_status?: string;
    submission_status?: string;
    forms_available?: string;
    error?: string;
  };
}

interface DetailedActivity {
  task_id: string;
  filename: string;
  status: string;
  total_websites: number;
  processed_websites: number;
  failed_websites: number;
  start_time: string;
  duration: string;
  activities: Activity[];
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'COMPLETED':
      return <CheckCircleIcon color="success" />;
    case 'IN_PROGRESS':
      return <PlayArrowIcon color="primary" />;
    case 'PENDING':
      return <PendingIcon color="warning" />;
    case 'FAILED':
      return <ErrorIcon color="error" />;
    default:
      return <InfoIcon color="info" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'COMPLETED':
      return 'success';
    case 'IN_PROGRESS':
      return 'primary';
    case 'PENDING':
      return 'warning';
    case 'FAILED':
      return 'error';
    default:
      return 'info';
  }
};

const DetailedActivityView: React.FC = () => {
  const [activities, setActivities] = useState<DetailedActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedTask, setExpandedTask] = useState<string | null>(null);
  const [selectedTaskForDetails, setSelectedTaskForDetails] = useState<string | null>(null);
  const [showWebsiteDetails, setShowWebsiteDetails] = useState(false);

  const fetchDetailedActivities = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/monitoring/detailed-activities');
      if (!response.ok) {
        throw new Error('Failed to fetch detailed activities');
      }
      const data = await response.json();
      setActivities(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetailedActivities();
  }, []);

  const handleTaskExpand = (taskId: string) => {
    setExpandedTask(expandedTask === taskId ? null : taskId);
  };

  const handleViewWebsiteDetails = (taskId: string) => {
    setSelectedTaskForDetails(taskId);
    setShowWebsiteDetails(true);
  };

  const handleCloseWebsiteDetails = () => {
    setShowWebsiteDetails(false);
    setSelectedTaskForDetails(null);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <IconButton color="inherit" size="small" onClick={fetchDetailedActivities}>
          <RefreshIcon />
        </IconButton>
      }>
        {error}
      </Alert>
    );
  }

  if (activities.length === 0) {
    return (
      <Alert severity="info">
        No active tasks found. Upload a file to see detailed activity tracking.
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" component="h2">
          Detailed Activity Tracking
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchDetailedActivities}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {activities.map((activity) => (
        <Card key={activity.task_id} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box>
                <Typography variant="h6" component="h3">
                  {activity.filename}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Task ID: {activity.task_id}
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip 
                  label={activity.status} 
                  color={getStatusColor(activity.status) as any}
                  size="small"
                />
                <Typography variant="body2" color="text.secondary">
                  {activity.duration}
                </Typography>
                <Tooltip title="View Individual Website Details">
                  <IconButton 
                    size="small" 
                    onClick={() => handleViewWebsiteDetails(activity.task_id)}
                    color="primary"
                  >
                    <VisibilityIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>

            <Box display="flex" gap={2} mb={2}>
              <Chip 
                label={`${activity.total_websites} Total`} 
                variant="outlined" 
                size="small"
              />
              <Chip 
                label={`${activity.processed_websites} Processed`} 
                color="success" 
                size="small"
              />
              <Chip 
                label={`${activity.failed_websites} Failed`} 
                color="error" 
                size="small"
              />
            </Box>

            <Accordion 
              expanded={expandedTask === activity.task_id}
              onChange={() => handleTaskExpand(activity.task_id)}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">
                  View Detailed Steps
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Stepper orientation="vertical">
                  {activity.activities.map((step, index) => (
                    <Step key={index} active={step.status === 'IN_PROGRESS'} completed={step.status === 'COMPLETED'}>
                      <StepLabel 
                        icon={getStatusIcon(step.status)}
                        error={step.status === 'FAILED'}
                      >
                        <Box>
                          <Typography variant="subtitle2">
                            {step.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {step.description}
                          </Typography>
                        </Box>
                      </StepLabel>
                      <StepContent>
                        <Box sx={{ mt: 1 }}>
                          {/* File Upload Details */}
                          {step.details.file_size && (
                            <List dense>
                              <ListItem>
                                <ListItemText 
                                  primary="File Size" 
                                  secondary={step.details.file_size}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText 
                                  primary="File Type" 
                                  secondary={step.details.file_type}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText 
                                  primary="Total Rows" 
                                  secondary={step.details.total_rows}
                                />
                              </ListItem>
                            </List>
                          )}

                          {/* File Processing Details */}
                          {step.details.validation && (
                            <List dense>
                              <ListItem>
                                <ListItemText 
                                  primary="Validation" 
                                  secondary={step.details.validation}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText 
                                  primary="Data Extraction" 
                                  secondary={step.details.data_extraction}
                                />
                              </ListItem>
                            </List>
                          )}

                          {/* Website Crawling Details */}
                          {step.details.total_websites && (
                            <Box>
                              <Typography variant="subtitle2" gutterBottom>
                                Crawling Progress
                              </Typography>
                              <Box display="flex" gap={1} mb={2}>
                                <Chip label={`Total: ${step.details.total_websites}`} size="small" />
                                <Chip label={`Processed: ${step.details.processed}`} color="success" size="small" />
                                <Chip label={`Failed: ${step.details.failed}`} color="error" size="small" />
                              </Box>
                              
                              {step.details.sample_websites && step.details.sample_websites.length > 0 && (
                                <Box>
                                  <Typography variant="subtitle2" gutterBottom>
                                    Sample Websites
                                  </Typography>
                                  {step.details.sample_websites.map((website, idx) => (
                                    <Card key={idx} variant="outlined" sx={{ mb: 1 }}>
                                      <CardContent sx={{ py: 1 }}>
                                        <Typography variant="body2" fontWeight="bold">
                                          {website.website}
                                        </Typography>
                                        <Chip 
                                          label={website.status} 
                                          size="small" 
                                          color={getStatusColor(website.status) as any}
                                          sx={{ mt: 0.5 }}
                                        />
                                        {website.data_collected && (
                                          <List dense sx={{ mt: 1 }}>
                                            <ListItem>
                                              <ListItemText 
                                                primary="Title" 
                                                secondary={website.data_collected.title}
                                              />
                                            </ListItem>
                                            <ListItem>
                                              <ListItemText 
                                                primary="Company" 
                                                secondary={website.data_collected.company_name}
                                              />
                                            </ListItem>
                                            <ListItem>
                                              <ListItemText 
                                                primary="Industry" 
                                                secondary={website.data_collected.industry}
                                              />
                                            </ListItem>
                                            <ListItem>
                                              <ListItemText 
                                                primary="Contact Form" 
                                                secondary={website.data_collected.contact_form}
                                              />
                                            </ListItem>
                                            <ListItem>
                                              <ListItemText 
                                                primary="About Us" 
                                                secondary={website.data_collected.about_us}
                                              />
                                            </ListItem>
                                          </List>
                                        )}
                                      </CardContent>
                                    </Card>
                                  ))}
                                </Box>
                              )}
                            </Box>
                          )}

                          {/* AI Generation Details */}
                          {step.details.ai_model && (
                            <List dense>
                              <ListItem>
                                <ListItemText 
                                  primary="AI Model" 
                                  secondary={step.details.ai_model}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText 
                                  primary="Message Type" 
                                  secondary={step.details.message_type}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText 
                                  primary="Generation Status" 
                                  secondary={step.details.generation_status}
                                />
                              </ListItem>
                            </List>
                          )}

                          {/* Form Submission Details */}
                          {step.details.submission_status && (
                            <List dense>
                              <ListItem>
                                <ListItemText 
                                  primary="Submission Status" 
                                  secondary={step.details.submission_status}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText 
                                  primary="Forms Available" 
                                  secondary={step.details.forms_available}
                                />
                              </ListItem>
                            </List>
                          )}

                          {/* Error Details */}
                          {step.details.error && (
                            <Alert severity="error" sx={{ mt: 1 }}>
                              {step.details.error}
                            </Alert>
                          )}
                        </Box>
                      </StepContent>
                    </Step>
                  ))}
                </Stepper>
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>
      ))}

      {/* Website Details Dialog */}
      <Dialog 
        open={showWebsiteDetails} 
        onClose={handleCloseWebsiteDetails}
        maxWidth="xl"
        fullWidth
      >
        <DialogTitle>
          Individual Website Details
          <IconButton
            aria-label="close"
            onClick={handleCloseWebsiteDetails}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
            }}
          >
            <ErrorIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedTaskForDetails && (
            <WebsiteDetailsView fileUploadId={selectedTaskForDetails} />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default DetailedActivityView; 