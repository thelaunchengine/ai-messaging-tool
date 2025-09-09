'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
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
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Badge
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Pending as PendingIcon,
  Error as ErrorIcon,
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Web as WebIcon,
  ContactSupport as ContactIcon,
  Business as BusinessIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

interface WebsiteDetail {
  website_url: string;
  status: string;
  crawling_timestamp: string;
  error_message?: string;
  crawling_attempts: {
    homepage: string;
    contact_page: string;
    about_page: string;
    meta_tags: string;
  };
  data_extracted: {
    title: string;
    company_name: string;
    industry: string;
    business_type: string;
    contact_form_url: string;
    about_us_content: string;
    meta_description: string;
  };
  contact_form_analysis: {
    found: boolean;
    url: string;
    form_type: string;
    submission_ready: boolean;
  };
  about_page_analysis: {
    found: boolean;
    content_length: number;
    content_preview: string;
    useful_for_ai: boolean;
  };
  crawling_performance: {
    response_time: string;
    page_size: string;
    http_status: string;
    robots_txt_respected: boolean;
    rate_limited: boolean;
  };
  data_quality: {
    has_company_name: boolean;
    has_industry: boolean;
    has_contact_form: boolean;
    has_about_content: boolean;
    completeness_score: string;
  };
}

interface WebsiteDetailsResponse {
  file_upload_id: string;
  summary: {
    total_websites: number;
    successful_crawls: number;
    failed_crawls: number;
    success_rate: string;
    contact_forms_found: number;
    about_pages_found: number;
    data_quality_average: string;
  };
  websites: WebsiteDetail[];
}

interface WebsiteDetailsViewProps {
  fileUploadId: string;
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

const WebsiteDetailsView: React.FC<WebsiteDetailsViewProps> = ({ fileUploadId }) => {
  const [data, setData] = useState<WebsiteDetailsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedWebsite, setExpandedWebsite] = useState<string | null>(null);

  const fetchWebsiteDetails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/monitoring/website-details/${fileUploadId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch website details');
      }
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (fileUploadId) {
      fetchWebsiteDetails();
    }
  }, [fileUploadId]);

  const handleWebsiteExpand = (websiteUrl: string) => {
    setExpandedWebsite(expandedWebsite === websiteUrl ? null : websiteUrl);
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
        <IconButton color="inherit" size="small" onClick={fetchWebsiteDetails}>
          <RefreshIcon />
        </IconButton>
      }>
        {error}
      </Alert>
    );
  }

  if (!data) {
    return (
      <Alert severity="info">
        No website details found for this upload.
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" component="h2">
          Individual Website Details
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchWebsiteDetails}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Summary Statistics */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Crawling Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary">
                  {data.summary.total_websites}
                </Typography>
                <Typography variant="body2">Total Websites</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {data.summary.successful_crawls}
                </Typography>
                <Typography variant="body2">Successful Crawls</Typography>
                <Typography variant="caption" color="text.secondary">
                  {data.summary.success_rate}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="error.main">
                  {data.summary.failed_crawls}
                </Typography>
                <Typography variant="body2">Failed Crawls</Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="info.main">
                  {data.summary.contact_forms_found}
                </Typography>
                <Typography variant="body2">Contact Forms Found</Typography>
              </Box>
            </Grid>
          </Grid>
          
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Data Quality: {data.summary.data_quality_average}
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={parseInt(data.summary.data_quality_average.split('(')[1].split('%')[0])}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Individual Website Details */}
      <Typography variant="h6" gutterBottom>
        Website Details ({data.websites.length} websites)
      </Typography>

      {data.websites.map((website, index) => (
        <Card key={index} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box>
                <Typography variant="h6" component="h3" sx={{ wordBreak: 'break-all' }}>
                  {website.website_url}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Crawled at: {new Date(website.crawling_timestamp).toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                {getStatusIcon(website.status)}
                <Chip 
                  label={website.status} 
                  color={getStatusColor(website.status) as any}
                  size="small"
                />
              </Box>
            </Box>

            {/* Quick Stats */}
            <Box display="flex" gap={1} mb={2} flexWrap="wrap">
              <Chip 
                icon={<BusinessIcon />}
                label={`Company: ${website.data_extracted.company_name !== 'Not found' ? 'Found' : 'Not found'}`}
                color={website.data_extracted.company_name !== 'Not found' ? 'success' : 'default'}
                size="small"
              />
              <Chip 
                icon={<ContactIcon />}
                label={`Contact: ${website.contact_form_analysis.found ? 'Found' : 'Not found'}`}
                color={website.contact_form_analysis.found ? 'success' : 'default'}
                size="small"
              />
              <Chip 
                icon={<InfoIcon />}
                label={`About: ${website.about_page_analysis.found ? 'Found' : 'Not found'}`}
                color={website.about_page_analysis.found ? 'success' : 'default'}
                size="small"
              />
              <Chip 
                icon={<AssessmentIcon />}
                label={website.data_quality.completeness_score}
                color="primary"
                size="small"
              />
            </Box>

            {/* Error Message if any */}
            {website.error_message && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {website.error_message}
              </Alert>
            )}

            <Accordion 
              expanded={expandedWebsite === website.website_url}
              onChange={() => handleWebsiteExpand(website.website_url)}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">
                  View Detailed Analysis
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={3}>
                  {/* Crawling Attempts */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Crawling Attempts
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Homepage" 
                          secondary={website.crawling_attempts.homepage}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Contact Page" 
                          secondary={website.crawling_attempts.contact_page}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="About Page" 
                          secondary={website.crawling_attempts.about_page}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Meta Tags" 
                          secondary={website.crawling_attempts.meta_tags}
                        />
                      </ListItem>
                    </List>
                  </Grid>

                  {/* Data Extracted */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Data Extracted
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Title" 
                          secondary={website.data_extracted.title}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Company Name" 
                          secondary={website.data_extracted.company_name}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Industry" 
                          secondary={website.data_extracted.industry}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Business Type" 
                          secondary={website.data_extracted.business_type}
                        />
                      </ListItem>
                    </List>
                  </Grid>

                  {/* Contact Form Analysis */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Contact Form Analysis
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Found" 
                          secondary={website.contact_form_analysis.found ? 'Yes' : 'No'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="URL" 
                          secondary={website.contact_form_analysis.url}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Form Type" 
                          secondary={website.contact_form_analysis.form_type}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Ready for Submission" 
                          secondary={website.contact_form_analysis.submission_ready ? 'Yes' : 'No'}
                        />
                      </ListItem>
                    </List>
                  </Grid>

                  {/* About Page Analysis */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      About Page Analysis
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Found" 
                          secondary={website.about_page_analysis.found ? 'Yes' : 'No'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Content Length" 
                          secondary={`${website.about_page_analysis.content_length} characters`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Useful for AI" 
                          secondary={website.about_page_analysis.useful_for_ai ? 'Yes' : 'No'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Content Preview" 
                          secondary={website.about_page_analysis.content_preview}
                        />
                      </ListItem>
                    </List>
                  </Grid>

                  {/* Crawling Performance */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Crawling Performance
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="HTTP Status" 
                          secondary={website.crawling_performance.http_status}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Response Time" 
                          secondary={website.crawling_performance.response_time}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Page Size" 
                          secondary={website.crawling_performance.page_size}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Robots.txt Respected" 
                          secondary={website.crawling_performance.robots_txt_respected ? 'Yes' : 'No'}
                        />
                      </ListItem>
                    </List>
                  </Grid>

                  {/* Data Quality */}
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Data Quality Assessment
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Has Company Name" 
                          secondary={website.data_quality.has_company_name ? 'Yes' : 'No'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Has Industry" 
                          secondary={website.data_quality.has_industry ? 'Yes' : 'No'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Has Contact Form" 
                          secondary={website.data_quality.has_contact_form ? 'Yes' : 'No'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Has About Content" 
                          secondary={website.data_quality.has_about_content ? 'Yes' : 'No'}
                        />
                      </ListItem>
                    </List>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default WebsiteDetailsView; 