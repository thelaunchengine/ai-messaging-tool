'use client';

import { useState, useEffect } from 'react';
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
  Alert,
  SelectChangeEvent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Card,
  CardContent,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Send as SendIcon,
  Message as MessageIcon,
  Visibility as VisibilityIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material';
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

interface Website {
  id: string;
  website_url: string;
  company_name: string;
  industry: string;
  business_type: string;
  generated_message?: string;
  message_status: string;
  scraping_status: string;
  created_at: string;
}

interface FileUpload {
  id: string;
  filename: string;
  total_websites: number;
  with_messages: number;
  without_messages: number;
  created_at: string;
}

interface MessageGenerationResult {
  website_id: string;
  website_url: string;
  company_name: string;
  generated_message: string;
  confidence_score: number;
  message_type: string;
  success: boolean;
  error?: string;
}

interface FormSubmissionResult {
  task_id: string;
  total_websites: number;
  message: string;
}

export default function ManualWorkflow() {
  const theme = useTheme();
  const [fileUploadId, setFileUploadId] = useState('');
  const [websites, setWebsites] = useState<Website[]>([]);
  const [selectedWebsites, setSelectedWebsites] = useState<string[]>([]);
  const [messageType, setMessageType] = useState('general');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showMessageDialog, setShowMessageDialog] = useState(false);
  const [selectedWebsiteForPreview, setSelectedWebsiteForPreview] = useState<Website | null>(null);
  const [messageResults, setMessageResults] = useState<MessageGenerationResult[]>([]);
  const [formSubmissionResult, setFormSubmissionResult] = useState<FormSubmissionResult | null>(null);
  const [userConfig, setUserConfig] = useState({
    sender_name: '',
    sender_email: '',
    sender_phone: '',
    message_subject: 'Business Inquiry',
    company_name: ''
  });

  // Load websites when file upload ID changes
  useEffect(() => {
    if (fileUploadId) {
      loadWebsites();
    }
  }, [fileUploadId]);

  const loadWebsites = async () => {
    if (!fileUploadId) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`/api/websites/by-file-upload/${fileUploadId}`);
      if (response.ok) {
        const data = await response.json();
        setWebsites(data.websites || []);
      } else {
        setError('Failed to load websites');
      }
    } catch (error) {
      setError('Error loading websites');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWebsiteSelection = (websiteId: string) => {
    setSelectedWebsites(prev => 
      prev.includes(websiteId) 
        ? prev.filter(id => id !== websiteId)
        : [...prev, websiteId]
    );
  };

  const handleSelectAll = () => {
    if (selectedWebsites.length === websites.length) {
      setSelectedWebsites([]);
    } else {
      setSelectedWebsites(websites.map(w => w.id));
    }
  };

  const generateMessages = async () => {
    if (selectedWebsites.length === 0) {
      setError('Please select at least one website');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('/api/message-generation/generate-for-selected', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          website_ids: selectedWebsites,
          message_type: messageType,
          user_id: 'default_user'
        })
      });

      if (response.ok) {
        const result = await response.json();
        setMessageResults(result.results || []);
        setSuccess(`Successfully generated messages for ${result.processed_websites} websites`);
        
        // Refresh websites to show updated message status
        await loadWebsites();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to generate messages');
      }
    } catch (error) {
      setError('Error generating messages');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitForms = async () => {
    if (selectedWebsites.length === 0) {
      setError('Please select at least one website');
      return;
    }

    if (!userConfig.sender_name || !userConfig.sender_email) {
      setError('Please fill in sender name and email');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch('/api/form-submission/submit-for-selected', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          website_ids: selectedWebsites,
          user_config: userConfig
        })
      });

      if (response.ok) {
        const result = await response.json();
        setFormSubmissionResult(result);
        setSuccess(`Form submission started for ${result.total_websites} websites`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to submit forms');
      }
    } catch (error) {
      setError('Error submitting forms');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const previewMessage = (website: Website) => {
    setSelectedWebsiteForPreview(website);
    setShowMessageDialog(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
      case 'GENERATED':
        return 'success';
      case 'PROCESSING':
      case 'PENDING':
        return 'warning';
      case 'FAILED':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
      case 'GENERATED':
        return <CheckCircleIcon color="success" />;
      case 'PROCESSING':
      case 'PENDING':
        return <InfoIcon color="warning" />;
      case 'FAILED':
        return <ErrorIcon color="error" />;
      default:
        return <InfoIcon />;
    }
  };

  return (
    <Grid container spacing={GRID_COMMON_SPACING}>
      <Grid xs={12}>
        <Typography variant="h3">Manual Workflow</Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
          Select websites, generate messages, and submit contact forms manually
        </Typography>
      </Grid>

      {/* File Upload ID Input */}
      <Grid xs={12}>
        <MainCard title="Load Websites">
          <Stack spacing={2}>
            <TextField
              fullWidth
              label="File Upload ID"
              value={fileUploadId}
              onChange={(e) => setFileUploadId(e.target.value)}
              placeholder="Enter the file upload ID from your CSV upload"
              helperText="Enter the file upload ID to load websites for manual processing"
            />
            <Button
              variant="contained"
              onClick={loadWebsites}
              disabled={!fileUploadId || loading}
              startIcon={<RefreshIcon />}
            >
              Load Websites
            </Button>
          </Stack>
        </MainCard>
      </Grid>

      {/* Alerts */}
      {error && (
        <Grid xs={12}>
          <Alert severity="error" onClose={() => setError('')}>
            {error}
          </Alert>
        </Grid>
      )}

      {success && (
        <Grid xs={12}>
          <Alert severity="success" onClose={() => setSuccess('')}>
            {success}
          </Alert>
        </Grid>
      )}

      {/* Message Generation Controls */}
      {websites.length > 0 && (
        <Grid xs={12}>
          <MainCard title="Message Generation">
            <Stack spacing={3}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Message Type</InputLabel>
                    <Select
                      value={messageType}
                      label="Message Type"
                      onChange={(e) => setMessageType(e.target.value)}
                    >
                      <MenuItem value="general">General Inquiry</MenuItem>
                      <MenuItem value="partnership">Partnership Proposal</MenuItem>
                      <MenuItem value="inquiry">Business Inquiry</MenuItem>
                      <MenuItem value="collaboration">Collaboration Request</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Typography variant="body2">
                      {selectedWebsites.length} websites selected
                    </Typography>
                    <Button
                      variant="outlined"
                      onClick={handleSelectAll}
                      size="small"
                    >
                      {selectedWebsites.length === websites.length ? 'Deselect All' : 'Select All'}
                    </Button>
                  </Stack>
                </Grid>
              </Grid>

              <Button
                variant="contained"
                onClick={generateMessages}
                disabled={selectedWebsites.length === 0 || loading}
                startIcon={<MessageIcon />}
              >
                Generate Messages for Selected Websites
              </Button>
            </Stack>
          </MainCard>
        </Grid>
      )}

      {/* Form Submission Controls */}
      {websites.length > 0 && (
        <Grid xs={12}>
          <MainCard title="Contact Form Submission">
            <Stack spacing={3}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Sender Name"
                    value={userConfig.sender_name}
                    onChange={(e) => setUserConfig({...userConfig, sender_name: e.target.value})}
                    required
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Sender Email"
                    type="email"
                    value={userConfig.sender_email}
                    onChange={(e) => setUserConfig({...userConfig, sender_email: e.target.value})}
                    required
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Sender Phone"
                    value={userConfig.sender_phone}
                    onChange={(e) => setUserConfig({...userConfig, sender_phone: e.target.value})}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Message Subject"
                    value={userConfig.message_subject}
                    onChange={(e) => setUserConfig({...userConfig, message_subject: e.target.value})}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Company Name"
                    value={userConfig.company_name}
                    onChange={(e) => setUserConfig({...userConfig, company_name: e.target.value})}
                  />
                </Grid>
              </Grid>

              <Button
                variant="contained"
                color="success"
                onClick={submitForms}
                disabled={selectedWebsites.length === 0 || loading || !userConfig.sender_name || !userConfig.sender_email}
                startIcon={<SendIcon />}
              >
                Submit Contact Forms for Selected Websites
              </Button>
            </Stack>
          </MainCard>
        </Grid>
      )}

      {/* Websites Table */}
      {websites.length > 0 && (
        <Grid xs={12}>
          <MainCard title={`Websites (${websites.length} total)`}>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedWebsites.length === websites.length}
                        indeterminate={selectedWebsites.length > 0 && selectedWebsites.length < websites.length}
                        onChange={handleSelectAll}
                      />
                    </TableCell>
                    <TableCell>Website</TableCell>
                    <TableCell>Company</TableCell>
                    <TableCell>Industry</TableCell>
                    <TableCell>Scraping Status</TableCell>
                    <TableCell>Message Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {websites.map((website) => (
                    <TableRow key={website.id}>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedWebsites.includes(website.id)}
                          onChange={() => handleWebsiteSelection(website.id)}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                          {website.website_url}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {website.company_name || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {website.industry || 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(website.scraping_status)}
                          label={website.scraping_status}
                          color={getStatusColor(website.scraping_status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(website.message_status)}
                          label={website.message_status}
                          color={getStatusColor(website.message_status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {website.generated_message && (
                          <Tooltip title="Preview generated message">
                            <IconButton
                              size="small"
                              onClick={() => previewMessage(website)}
                            >
                              <VisibilityIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </MainCard>
        </Grid>
      )}

      {/* Loading Indicator */}
      {loading && (
        <Grid xs={12}>
          <Paper sx={{ p: 2 }}>
            <Stack direction="row" spacing={2} alignItems="center">
              <LinearProgress sx={{ flexGrow: 1 }} />
              <Typography variant="body2">Processing...</Typography>
            </Stack>
          </Paper>
        </Grid>
      )}

      {/* Message Preview Dialog */}
      <Dialog
        open={showMessageDialog}
        onClose={() => setShowMessageDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Generated Message Preview
          <Typography variant="body2" color="text.secondary">
            {selectedWebsiteForPreview?.company_name} - {selectedWebsiteForPreview?.website_url}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedWebsiteForPreview?.generated_message ? (
            <Paper variant="outlined" sx={{ p: 2, mt: 1 }}>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {selectedWebsiteForPreview.generated_message}
              </Typography>
            </Paper>
          ) : (
            <Typography variant="body1" color="text.secondary">
              No message generated for this website.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMessageDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Grid>
  );
} 