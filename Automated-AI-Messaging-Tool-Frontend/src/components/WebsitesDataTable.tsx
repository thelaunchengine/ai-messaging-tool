'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { debounce } from 'lodash';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
  TextField,
  InputAdornment,
  IconButton,
  Chip,
  Typography,
  CircularProgress,
  Alert,
  Collapse,
  Grid,
  Divider
} from '@mui/material';
import { Search, Refresh, ExpandMore, ExpandLess } from '@mui/icons-material';

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
  createdAt: string;
  updatedAt: string;
}

interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  pages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

interface WebsitesDataTableProps {
  fileUploadId: string;
}

export default function WebsitesDataTable({ fileUploadId }: WebsitesDataTableProps) {
  const [websites, setWebsites] = useState<Website[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    limit: 10,
    total: 0,
    pages: 0,
    hasNext: false,
    hasPrev: false
  });
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const fetchWebsites = async (page: number = 1, searchTerm: string = '', sortField: string = sortBy, order: 'asc' | 'desc' = sortOrder) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: pagination.limit.toString(),
        search: searchTerm,
        sortBy: sortField,
        sortOrder: order
      });

      const response = await fetch(`/api/upload/${fileUploadId}/websites?${params}`);
      if (!response.ok) {
        throw new Error('Failed to fetch websites');
      }

      const data = await response.json();
      setWebsites(data.websites);
      setPagination(data.pagination);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWebsites();
  }, [fileUploadId]);

  const handlePageChange = (event: unknown, newPage: number) => {
    fetchWebsites(newPage + 1, search, sortBy, sortOrder);
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearch(value);
    // Debounce search with proper cleanup
    const timeoutId = setTimeout(() => {
      fetchWebsites(1, value, sortBy, sortOrder);
    }, 500);
    return () => clearTimeout(timeoutId);
  };

  // Memoize the search handler to prevent unnecessary re-renders
  const debouncedSearch = useCallback(
    debounce((value: string) => {
      fetchWebsites(1, value, sortBy, sortOrder);
    }, 500),
    [sortBy, sortOrder]
  );

  const handleRefresh = () => {
    fetchWebsites(pagination.page, search, sortBy, sortOrder);
  };

  const handleRowExpand = (websiteId: string) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(websiteId)) {
      newExpandedRows.delete(websiteId);
    } else {
      newExpandedRows.add(websiteId);
    }
    setExpandedRows(newExpandedRows);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'PENDING':
        return 'warning';
      case 'FAILED':
        return 'error';
      case 'PROCESSING':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const truncateText = (text: string, maxLength: number = 50) => {
    if (!text) return '';
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  const ExpandedRowDetails = ({ website }: { website: Website }) => (
    <TableRow>
      <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
        <Collapse in={expandedRows.has(website.id)} timeout="auto" unmountOnExit>
          <Box sx={{ margin: 1, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Grid container spacing={3}>
              {/* Basic Information */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Basic Information</Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Website URL:</Typography>
                  <Typography variant="body1" sx={{ wordBreak: 'break-all', mb: 1 }}>
                    {website.websiteUrl}
                  </Typography>
                </Box>
                {website.contactFormUrl && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Contact Form URL:</Typography>
                    <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                      {website.contactFormUrl}
                    </Typography>
                  </Box>
                )}
                {website.companyName && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Company Name:</Typography>
                    <Typography variant="body1">{website.companyName}</Typography>
                  </Box>
                )}
                {website.businessType && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Business Type:</Typography>
                    <Typography variant="body1">{website.businessType}</Typography>
                  </Box>
                )}
                {website.industry && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Industry:</Typography>
                    <Typography variant="body1">{website.industry}</Typography>
                  </Box>
                )}
              </Grid>

              {/* Status Information */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Status Information</Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Scraping Status:</Typography>
                  <Chip 
                    label={website.scrapingStatus} 
                    size="small" 
                    color={getStatusColor(website.scrapingStatus) as any}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Message Status:</Typography>
                  <Chip 
                    label={website.messageStatus} 
                    size="small" 
                    color={getStatusColor(website.messageStatus) as any}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Has Contact Form:</Typography>
                  <Chip 
                    label={website.hasContactForm ? 'Yes' : 'No'} 
                    size="small" 
                    color={website.hasContactForm ? 'success' : 'default' as any}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Response Received:</Typography>
                  <Chip 
                    label={website.responseReceived ? 'Yes' : 'No'} 
                    size="small" 
                    color={website.responseReceived ? 'success' : 'default' as any}
                    sx={{ mt: 0.5 }}
                  />
                </Box>
              </Grid>

              {/* Content Information */}
              {website.aboutUsContent && (
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>About Us Content</Typography>
                  <Typography variant="body2" sx={{ 
                    bgcolor: 'white', 
                    p: 2, 
                    borderRadius: 1, 
                    border: '1px solid #e0e0e0',
                    maxHeight: 200,
                    overflow: 'auto'
                  }}>
                    {website.aboutUsContent}
                  </Typography>
                </Grid>
              )}

              {/* Message Information */}
              {(website.generatedMessage || website.sentMessage) && (
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>Message Information</Typography>
                  {website.generatedMessage && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">Generated Message:</Typography>
                      <Typography variant="body2" sx={{ 
                        bgcolor: 'white', 
                        p: 2, 
                        borderRadius: 1, 
                        border: '1px solid #e0e0e0',
                        maxHeight: 150,
                        overflow: 'auto'
                      }}>
                        {website.generatedMessage}
                      </Typography>
                    </Box>
                  )}
                  {website.sentMessage && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">Sent Message:</Typography>
                      <Typography variant="body2" sx={{ 
                        bgcolor: 'white', 
                        p: 2, 
                        borderRadius: 1, 
                        border: '1px solid #e0e0e0',
                        maxHeight: 150,
                        overflow: 'auto'
                      }}>
                        {website.sentMessage}
                      </Typography>
                    </Box>
                  )}
                  {website.sentAt && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">Sent At:</Typography>
                      <Typography variant="body2">{formatDate(website.sentAt)}</Typography>
                    </Box>
                  )}
                </Grid>
              )}

              {/* Response Information */}
              {website.responseContent && (
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>Response Content</Typography>
                  <Typography variant="body2" sx={{ 
                    bgcolor: 'white', 
                    p: 2, 
                    borderRadius: 1, 
                    border: '1px solid #e0e0e0',
                    maxHeight: 200,
                    overflow: 'auto'
                  }}>
                    {website.responseContent}
                  </Typography>
                </Grid>
              )}

              {/* Error Information */}
              {website.errorMessage && (
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom color="error">Error Information</Typography>
                  <Typography variant="body2" sx={{ 
                    bgcolor: '#ffebee', 
                    p: 2, 
                    borderRadius: 1, 
                    border: '1px solid #f44336',
                    color: '#d32f2f'
                  }}>
                    {website.errorMessage}
                  </Typography>
                </Grid>
              )}

              {/* Timestamps */}
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>Timestamps</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">Created:</Typography>
                    <Typography variant="body2">{formatDate(website.createdAt)}</Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">Updated:</Typography>
                    <Typography variant="body2">{formatDate(website.updatedAt)}</Typography>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </Box>
        </Collapse>
      </TableCell>
    </TableRow>
  );

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ bgcolor: 'background.paper', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
      {/* Header with search and refresh */}
      <Box sx={{ p: 3, pb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          Website Data ({pagination.total.toLocaleString()} entries)
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            size="small"
            placeholder="Search websites..."
            value={search}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 250 }}
          />
          <IconButton onClick={handleRefresh} disabled={loading}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Loading indicator */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Data table */}
      {!loading && (
        <>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold', width: 50 }}></TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Website URL</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Contact Form</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Company</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Industry</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Scraping Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Message Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Created</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {websites.map((website) => (
                  <React.Fragment key={website.id}>
                    <TableRow>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => handleRowExpand(website.id)}
                          sx={{ 
                            p: 0,
                            color: expandedRows.has(website.id) ? 'primary.main' : 
                                   (website.aboutUsContent || website.generatedMessage || website.responseContent || website.errorMessage) ? 'info.main' : 'text.secondary',
                            '&:hover': {
                              color: 'primary.main'
                            }
                          }}
                          title={expandedRows.has(website.id) ? 'Collapse details' : 
                                 (website.aboutUsContent || website.generatedMessage || website.responseContent || website.errorMessage) ? 'Expand details (has additional info)' : 'Expand details'}
                        >
                          {expandedRows.has(website.id) ? <ExpandLess /> : <ExpandMore />}
                        </IconButton>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                          {website.websiteUrl}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {website.contactFormUrl ? (
                          <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                            {truncateText(website.contactFormUrl, 40)}
                          </Typography>
                        ) : (
                          <Chip label="No Contact Form" size="small" color="default" />
                        )}
                      </TableCell>
                      <TableCell>
                        {website.companyName ? (
                          <Typography variant="body2">
                            {truncateText(website.companyName, 30)}
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {website.industry ? (
                          <Typography variant="body2">
                            {truncateText(website.industry, 20)}
                          </Typography>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            -
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={website.scrapingStatus} 
                          size="small" 
                          color={getStatusColor(website.scrapingStatus) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={website.messageStatus} 
                          size="small" 
                          color={getStatusColor(website.messageStatus) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(website.createdAt)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                    <ExpandedRowDetails website={website} />
                  </React.Fragment>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          <TablePagination
            component="div"
            count={pagination.total}
            page={pagination.page - 1}
            onPageChange={handlePageChange}
            rowsPerPage={pagination.limit}
            rowsPerPageOptions={[10, 25, 50, 100]}
            onRowsPerPageChange={(event) => {
              const newLimit = parseInt(event.target.value, 10);
              setPagination(prev => ({ ...prev, limit: newLimit }));
              fetchWebsites(1, search, sortBy, sortOrder);
            }}
            labelDisplayedRows={({ from, to, count }) =>
              `${from}-${to} of ${count !== -1 ? count : `more than ${to}`}`
            }
          />
        </>
      )}
    </Box>
  );
} 