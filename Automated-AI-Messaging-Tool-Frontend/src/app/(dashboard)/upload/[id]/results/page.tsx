'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Stack,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Card,
  CardContent,
  Grid,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  TablePagination
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  ContentCopy as CopyIcon,
  SmartToy as AIIcon
} from '@mui/icons-material';
import { useRouter, useParams } from 'next/navigation';
import MainCard from '../../../../../components/MainCard';

interface Website {
  id: string;
  websiteUrl: string;
  contactFormUrl?: string;
  hasContactForm: boolean;
  companyName?: string;
  businessType?: string;
  industry?: string;
  aboutUsContent?: string;
  scrapingStatus: string;
  messageStatus: string;
  generatedMessage?: string;
  sentMessage?: string;
  sentAt?: string;
  responseReceived: boolean;
  responseContent?: string;
  errorMessage?: string;
  // New contact form submission fields
  submissionStatus?: string;
  submissionError?: string;
  submittedFormFields?: any;
  submissionResponse?: string;
  createdAt: string;
  updatedAt: string;
}

const ResultsPage = () => {
  const router = useRouter();
  const params = useParams();
  const fileUploadId = params.id as string;

  const [websites, setWebsites] = useState<Website[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalWebsites, setTotalWebsites] = useState(0);
  const [websitesPerPage, setWebsitesPerPage] = useState(50);
  
  // Overall statistics state
  const [statistics, setStatistics] = useState({
    totalWebsites: 0,
    scrapedSuccessfully: 0,
    failed: 0,
    contactFormsSubmitted: 0
  });

  // AI Message Generation State
  const [aiDialogOpen, setAiDialogOpen] = useState(false);
  const [selectedWebsite, setSelectedWebsite] = useState<Website | null>(null);
  const [aiMessageType, setAiMessageType] = useState('general');
  const [customPrompt, setCustomPrompt] = useState('');
  const [generatingMessage, setGeneratingMessage] = useState(false);
  const [generatedMessage, setGeneratedMessage] = useState<string>('');
  const [generationError, setGenerationError] = useState<string | null>(null);

  const fetchWebsites = async (page: number = currentPage, limit: number = websitesPerPage) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/upload/${fileUploadId}/websites?page=${page}&limit=${limit}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setWebsites(data.websites || []);
        setTotalPages(data.pagination?.pages || 1);
        setTotalWebsites(data.pagination?.total || 0);
        
        // Set overall statistics
        if (data.statistics) {
          setStatistics(data.statistics);
        }
      } else {
        setError('Failed to fetch website results');
      }
    } catch (err) {
      setError('Error loading website results');
      console.error('Error fetching websites:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (fileUploadId) {
      fetchWebsites();
    }
  }, [fileUploadId]);

  // Pagination handlers
  const handlePageChange = (event: React.ChangeEvent<unknown>, page: number) => {
    setCurrentPage(page);
    fetchWebsites(page, websitesPerPage);
  };

  const handlePerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newPerPage = parseInt(event.target.value);
    setWebsitesPerPage(newPerPage);
    setCurrentPage(1);
    fetchWebsites(1, newPerPage);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'pending':
        return 'info';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircleIcon color="success" />;
      case 'processing':
        return <PendingIcon color="warning" />;
      case 'pending':
        return <PendingIcon color="info" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      default:
        return <PendingIcon color="default" />;
    }
  };

  const getContactFormStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'submitted':
        return 'success';
      case 'submitting':
        return 'warning';
      case 'pending':
        return 'info';
      case 'failed':
        return 'error';
      case 'no_form_found':
        return 'default';
      default:
        return 'default';
    }
  };

  const getContactFormStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'submitted':
        return <CheckCircleIcon color="success" />;
      case 'submitting':
        return <PendingIcon color="warning" />;
      case 'pending':
        return <PendingIcon color="info" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'no_form_found':
        return <PendingIcon color="default" />;
      default:
        return <PendingIcon color="default" />;
    }
  };

  const getContactFormStatusText = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'submitted':
        return 'SUCCESS';
      case 'submitting':
        return 'SUBMITTING';
      case 'pending':
        return 'PENDING';
      case 'failed':
        return 'FAILED';
      case 'no_form_found':
        return 'NO FORM FOUND';
      default:
        return 'PENDING';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    const yyyy = date.getFullYear();
    return `${mm}/${dd}/${yyyy}`;
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setSuccessMessage('Copied to clipboard!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      setError('Failed to copy to clipboard');
    }
  };

  const copyGeneratedMessage = async () => {
    try {
      await navigator.clipboard.writeText(generatedMessage);
      setSuccessMessage('Generated message copied to clipboard!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Failed to copy generated message:', err);
      setError('Failed to copy generated message');
    }
  };

  const handleRefresh = async () => {
    await fetchWebsites();
    setSuccessMessage('Results refreshed successfully.');
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  // AI Message Generation Functions
  const openAiDialog = (website: Website) => {
    setSelectedWebsite(website);
    setAiMessageType('general');
    setCustomPrompt('');
    setGeneratedMessage('');
    setGenerationError(null);
    setAiDialogOpen(true);
  };

  const closeAiDialog = () => {
    setAiDialogOpen(false);
    setSelectedWebsite(null);
    setGeneratingMessage(false);
  };

  const generateAiMessage = async () => {
    if (!selectedWebsite) return;

    try {
      setGeneratingMessage(true);
      setGenerationError(null);

      const response = await fetch('/api/message-generation/generate-for-selected', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          ai_model: 'gemini',
          message_type: aiMessageType,
          custom_prompt: customPrompt,
          website_data: [selectedWebsite]
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.messages && data.messages.length > 0) {
          const message = data.messages[0].message;
          setGeneratedMessage(message);
          
          // Update the website in the local state
          setWebsites(prevWebsites => 
            prevWebsites.map(w => 
              w.id === selectedWebsite.id 
                ? { ...w, generatedMessage: message, messageStatus: 'GENERATED' }
                : w
            )
          );
          
          setSuccessMessage('AI message generated successfully!');
          setTimeout(() => setSuccessMessage(''), 3000);
        } else {
          setGenerationError('Failed to generate message. Please try again.');
        }
      } else {
        const errorData = await response.json();
        setGenerationError(errorData.message || 'Failed to generate message');
      }
    } catch (err) {
      console.error('Error generating AI message:', err);
      setGenerationError('Error generating message. Please try again.');
    } finally {
      setGeneratingMessage(false);
    }
  };



  if (loading) {
    return (
      <Box sx={{ p: { xs: 2, md: 4 }, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => router.back()}
        >
          Back
        </Button>
        <Button variant="outlined" onClick={handleRefresh}>
          Refresh
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {successMessage}
        </Alert>
      )}

      <MainCard>
        <Typography variant="h6" gutterBottom>
          File Upload ID: {fileUploadId}
        </Typography>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Websites
                </Typography>
                <Typography variant="h4">{statistics.totalWebsites.toLocaleString()}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Scraped Successfully
                </Typography>
                <Typography variant="h4">{statistics.scrapedSuccessfully.toLocaleString()}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Failed
                </Typography>
                <Typography variant="h4">
                  {statistics.failed.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Contact Forms Submitted
                </Typography>
                <Typography variant="h4">
                  {statistics.contactFormsSubmitted.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Pagination Controls */}
        {totalWebsites > 0 && (
          <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1, mb: 2 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
              <Typography variant="body2" color="text.secondary">
                Showing {websites.length} of {totalWebsites.toLocaleString()} websites
              </Typography>
              <Stack direction="row" alignItems="center" spacing={2}>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Per Page</InputLabel>
                  <Select
                    value={websitesPerPage}
                    label="Per Page"
                    onChange={handlePerPageChange}
                  >
                    <MenuItem value={25}>25</MenuItem>
                    <MenuItem value={50}>50</MenuItem>
                    <MenuItem value={100}>100</MenuItem>
                    <MenuItem value={200}>200</MenuItem>
                  </Select>
                </FormControl>
                <Pagination
                  count={totalPages}
                  page={currentPage}
                  onChange={handlePageChange}
                  color="primary"
                  size="small"
                  showFirstButton
                  showLastButton
                />
              </Stack>
            </Stack>
          </Box>
        )}

        {websites.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No websites found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              No websites have been processed for this upload yet
            </Typography>
          </Box>
        ) : (
          <Stack spacing={2}>
            {websites.map((website, index) => (
              <Accordion key={website.id}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Stack direction="row" spacing={2} alignItems="center" sx={{ width: '100%' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', minWidth: 200 }}>
                      {getStatusIcon(website.scrapingStatus)}
                      <Typography variant="subtitle1" sx={{ ml: 1, fontWeight: 'bold', color: 'black' }}>
                        {website.websiteUrl}
                      </Typography>
                    </Box>
                    <Stack direction="row" spacing={1}>
                      <Chip
                        label={`Scraping: ${website.scrapingStatus}`}
                        color={getStatusColor(website.scrapingStatus) as any}
                        size="small"
                      />
                      <Chip
                        label={`Message: ${website.messageStatus}`}
                        color={getStatusColor(website.messageStatus) as any}
                        size="small"
                      />
                      <Chip
                        label={`Contact Form: ${getContactFormStatusText(website.submissionStatus)}`}
                        color={getContactFormStatusColor(website.submissionStatus) as any}
                        size="small"
                      />
                    </Stack>
                  </Stack>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>
                        Company Information
                      </Typography>
                      <Stack spacing={1}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Company Name:
                          </Typography>
                          <Typography variant="body1">{website.companyName || 'Not found'}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Industry:
                          </Typography>
                          <Typography variant="body1">{website.industry || 'Not found'}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Business Type:
                          </Typography>
                          <Typography variant="body1">{website.businessType || 'Not found'}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Contact Form:
                          </Typography>
                          <Typography variant="body1">
                            {website.contactFormUrl ? (
                              <Box>
                                <Typography variant="body2" component="span">
                                  {website.contactFormUrl}
                                </Typography>
                                <Tooltip title="Copy URL">
                                  <IconButton 
                                    size="small" 
                                    onClick={() => copyToClipboard(website.contactFormUrl!)}
                                    sx={{ ml: 1 }}
                                  >
                                    <CopyIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </Box>
                            ) : (
                              'Not found'
                            )}
                          </Typography>
                        </Box>
                      </Stack>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>
                        About Us Content
                      </Typography>
                      <Box sx={{ maxHeight: 200, overflow: 'auto', border: 1, borderColor: 'divider', p: 1, borderRadius: 1 }}>
                        <Typography variant="body2">{website.aboutUsContent || 'No content scraped'}</Typography>
                      </Box>
                    </Grid>

                    <Grid item xs={12}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h6">
                          Generated Message
                        </Typography>
                        <Button
                          variant="contained"
                          startIcon={<AIIcon />}
                          onClick={() => openAiDialog(website)}
                          disabled={website.scrapingStatus !== 'COMPLETED'}
                          size="small"
                        >
                          Generate AI Message
                        </Button>
                      </Stack>
                      <Box sx={{ 
                        maxHeight: 300, 
                        overflow: 'auto', 
                        border: 1, 
                        borderColor: 'divider', 
                        p: 2, 
                        borderRadius: 1,
                        backgroundColor: website.generatedMessage ? 'background.paper' : 'grey.50'
                      }}>
                        {website.generatedMessage ? (
                          <Box>
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                              {website.generatedMessage}
                            </Typography>
                            <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-end' }}>
                              <Tooltip title="Copy Message">
                                <IconButton 
                                  size="small" 
                                  onClick={() => copyToClipboard(website.generatedMessage!)}
                                >
                                  <CopyIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            {website.messageStatus === 'FAILED' ? 'Message generation failed' : 
                             website.messageStatus === 'PENDING' ? 'Message generation pending' : 
                             'No message generated'}
                          </Typography>
                        )}
                      </Box>
                      
                      {/* Contact Form Submission Details */}
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                          Contact Form Submission
                        </Typography>
                        <Box sx={{ 
                          border: 1, 
                          borderColor: 'divider', 
                          p: 2, 
                          borderRadius: 1,
                          backgroundColor: 'background.paper'
                        }}>
                          <Stack spacing={2}>
                            {/* Submission Status */}
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {getContactFormStatusIcon(website.submissionStatus)}
                              <Typography variant="body2">
                                Status: <strong>{getContactFormStatusText(website.submissionStatus)}</strong>
                              </Typography>
                            </Box>
                            
                            {/* Form Link */}
                            {website.contactFormUrl && (
                              <Box>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  Form URL:
                                </Typography>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Typography variant="body2" component="span" sx={{ fontFamily: 'monospace' }}>
                                    {website.contactFormUrl}
                                  </Typography>
                                  <Tooltip title="Copy URL">
                                    <IconButton 
                                      size="small" 
                                      onClick={() => copyToClipboard(website.contactFormUrl!)}
                                    >
                                      <CopyIcon fontSize="small" />
                                    </IconButton>
                                  </Tooltip>
                                </Box>
                              </Box>
                            )}
                            
                            {/* Submitted Form Fields */}
                            {website.submittedFormFields ? (
                              <Box>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  Submitted Fields:
                                </Typography>
                                <Box sx={{ 
                                  backgroundColor: 'success.light', 
                                  p: 1, 
                                  borderRadius: 1,
                                  fontFamily: 'monospace',
                                  fontSize: '0.875rem'
                                }}>
                                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                                    {JSON.stringify(website.submittedFormFields, null, 2)}
                                  </pre>
                                </Box>
                              </Box>
                            ) : website.submissionStatus === 'FAILED' && (
                              <Box>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  Submitted Fields:
                                </Typography>
                                <Typography variant="body2" color="error.main" sx={{ 
                                  backgroundColor: 'error.light', 
                                  p: 1, 
                                  borderRadius: 1,
                                  fontStyle: 'italic'
                                }}>
                                  No fields submitted - Form submission failed
                                </Typography>
                              </Box>
                            )}
                            
                            {/* Submission Response */}
                            {website.submissionResponse && (
                              <Box>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  Submission Response:
                                </Typography>
                                <Typography variant="body2" sx={{ 
                                  backgroundColor: 'grey.50', 
                                  p: 1, 
                                  borderRadius: 1,
                                  fontFamily: 'monospace'
                                }}>
                                  {website.submissionResponse}
                                </Typography>
                              </Box>
                            )}
                            
                            {/* Error Message */}
                            {website.submissionError && (
                              <Box>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                  Error:
                                </Typography>
                                <Alert severity="error" sx={{ py: 0 }}>
                                  <Typography variant="body2">
                                    {website.submissionError}
                                  </Typography>
                                </Alert>
                              </Box>
                            )}
                            
                            {/* No Form Found */}
                            {website.submissionStatus === 'NO_FORM_FOUND' && (
                              <Typography variant="body2" color="text.secondary">
                                No contact form was detected on this website.
                              </Typography>
                            )}
                          </Stack>
                        </Box>
                      </Box>
                    </Grid>

                    {website.errorMessage && (
                      <Grid item xs={12}>
                        <Alert severity="error">
                          <Typography variant="body2">Error: {website.errorMessage}</Typography>
                        </Alert>
                      </Grid>
                    )}

                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">
                        Created: {formatDate(website.createdAt)} | Updated: {formatDate(website.updatedAt)}
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        )}

        {/* Bottom Pagination Controls */}
        {totalWebsites > 0 && totalPages > 1 && (
          <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1, mt: 2 }}>
            <Stack direction="row" justifyContent="center" alignItems="center" spacing={2}>
              <Typography variant="body2" color="text.secondary">
                Page {currentPage} of {totalPages}
              </Typography>
              <Pagination
                count={totalPages}
                page={currentPage}
                onChange={handlePageChange}
                color="primary"
                size="small"
                showFirstButton
                showLastButton
              />
            </Stack>
          </Box>
        )}
      </MainCard>

      {/* AI Message Generation Dialog */}
      <Dialog 
        open={aiDialogOpen} 
        onClose={closeAiDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Generate AI Message for {selectedWebsite?.websiteUrl}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Message Type</InputLabel>
              <Select
                value={aiMessageType}
                label="Message Type"
                onChange={(e) => setAiMessageType(e.target.value)}
              >
                <MenuItem value="general">General Outreach</MenuItem>
                <MenuItem value="partnership">Partnership Proposal</MenuItem>
                <MenuItem value="support">Support Inquiry</MenuItem>
                <MenuItem value="custom">Custom Message</MenuItem>
              </Select>
            </FormControl>

            {aiMessageType === 'custom' && (
              <TextField
                fullWidth
                label="Custom Prompt"
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Describe what kind of message you want to generate..."
                multiline
                rows={3}
              />
            )}

            {generationError && (
              <Alert severity="error">
                {generationError}
              </Alert>
            )}

            {generatedMessage && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Generated Message:
                </Typography>
                <Box sx={{ 
                  maxHeight: 300, 
                  overflow: 'auto', 
                  border: 1, 
                  borderColor: 'divider', 
                  p: 2, 
                  borderRadius: 1,
                  backgroundColor: 'background.paper'
                }}>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {generatedMessage}
                  </Typography>
                </Box>
                <Box sx={{ mt: 1, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="outlined"
                    startIcon={<CopyIcon />}
                    onClick={copyGeneratedMessage}
                    size="small"
                  >
                    Copy Message
                  </Button>
                </Box>
              </Box>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeAiDialog}>
            Close
          </Button>
          <Button
            onClick={generateAiMessage}
            variant="contained"
            disabled={generatingMessage || (aiMessageType === 'custom' && !customPrompt.trim())}
            startIcon={generatingMessage ? <CircularProgress size={16} /> : <AIIcon />}
          >
            {generatingMessage ? 'Generating...' : 'Generate Message'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ResultsPage;
