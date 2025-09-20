'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { normalizeStatus, getStatusColor } from '../../../utils/statusUtils';

interface FileUpload {
  id: string;
  filename: string;
  originalName: string;
  fileSize: number;
  fileType: string;
  status: string;
  totalWebsites: number;
  processedWebsites: number;
  failedWebsites: number;
  createdAt: string;
  updatedAt: string;
  users?: {
    name: string;
    email: string;
  };
}

interface PaginationInfo {
  page: number;
  limit: number;
  totalCount: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPrevPage: boolean;
}

export default function HistoryPage() {
  const router = useRouter();
  const [fileUploads, setFileUploads] = useState<FileUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    limit: 10,
    totalCount: 0,
    totalPages: 0,
    hasNextPage: false,
    hasPrevPage: false
  });
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('all');
  const [rowsPerPage] = useState(10);

  // Use the correct user ID that has data in the database
  const userId = 'cmdi7lqnj0000sbp8h98vwlco';

  const fetchFileUploads = async (pageNum = 1, searchTerm = '', statusFilter = 'all') => {
    try {
      setLoading(true);
      setError(null);

      // Always use the working user ID
      let url = `/api/upload?userId=${userId}`;

      if (statusFilter !== 'all') {
        // When filtering by status, fetch ALL data first, then filter and paginate on frontend
        const params = [
          `page=1`,
          `limit=1000`, // Fetch a large number to get all records
          `search=${searchTerm}`
        ];
        url += `&${params.join('&')}`;
      } else {
        // When showing all status, use normal pagination
        const params = [
          `page=${pageNum}`,
          `limit=${rowsPerPage}`,
          `search=${searchTerm}`
        ];
        url += `&${params.join('&')}`;
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.fileUploads && Array.isArray(data.fileUploads)) {
        let filteredUploads = data.fileUploads;
        
        if (statusFilter !== 'all') {
          // Filter by status
          filteredUploads = data.fileUploads.filter((upload: any) => 
            normalizeStatus(upload.status).status === statusFilter
          );
          
          // Apply pagination to filtered results
          const startIndex = (pageNum - 1) * rowsPerPage;
          const endIndex = startIndex + rowsPerPage;
          const paginatedUploads = filteredUploads.slice(startIndex, endIndex);
          
          setFileUploads(paginatedUploads);
          setPagination({
            page: pageNum,
            limit: rowsPerPage,
            totalCount: filteredUploads.length,
            totalPages: Math.ceil(filteredUploads.length / rowsPerPage),
            hasNextPage: endIndex < filteredUploads.length,
            hasPrevPage: pageNum > 1
          });
        } else {
          // No filtering, use API pagination
          setFileUploads(filteredUploads);
          setPagination(data.pagination || {
            page: pageNum,
            limit: rowsPerPage,
            totalCount: filteredUploads.length,
            totalPages: Math.ceil(filteredUploads.length / rowsPerPage),
            hasNextPage: false,
            hasPrevPage: pageNum > 1
          });
        }
      } else {
        console.error('Invalid data structure:', data);
        setFileUploads([]);
        setPagination({
          page: pageNum,
          limit: rowsPerPage,
          totalCount: 0,
          totalPages: 0,
          hasNextPage: false,
          hasPrevPage: false
        });
      }
    } catch (err) {
      console.error('Error fetching file uploads:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch file uploads');
      setFileUploads([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFileUploads(1, search, status);
  }, [search, status]);

  const handlePageChange = (event: React.ChangeEvent<unknown>, newPage: number) => {
    fetchFileUploads(newPage, search, status);
  };

  const handleSearch = () => {
    fetchFileUploads(1, search, status);
  };

  const handleStatusChange = (newStatus: string) => {
    setStatus(newStatus);
    // Trigger refetch with new status filter
    fetchFileUploads(1, search, newStatus);
  };

  const handleRefresh = () => {
    fetchFileUploads(pagination.page, search, status);
  };

  const handleViewResults = (uploadId: string) => {
    router.push(`/upload/${uploadId}/results`);
  };

  // Normalize detailed status to generic status for filtering

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading && fileUploads.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        File Upload History
      </Typography>

      {/* Search and Filter Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
            <TextField
              label="Search files"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              size="small"
              sx={{ minWidth: 200 }}
            />
            
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={status}
                label="Status"
                onChange={(e) => handleStatusChange(e.target.value)}
              >
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="processing">Processing</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="error">Error</MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="contained"
              onClick={handleSearch}
              startIcon={<SearchIcon />}
            >
              Search
            </Button>

            <Button
              variant="outlined"
              onClick={handleRefresh}
              startIcon={<RefreshIcon />}
            >
              Refresh
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results Summary */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Showing {fileUploads.length} of {pagination.totalCount} uploads
        </Typography>
      </Box>

      {/* File Uploads Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>File Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Websites</TableCell>
              <TableCell>Upload Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {fileUploads.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body2" color="text.secondary">
                    {loading ? 'Loading...' : 'No file uploads found'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              fileUploads.map((upload) => (
                <TableRow key={upload.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {upload.originalName}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      ID: {upload.id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={upload.fileType ? upload.fileType.toUpperCase() : 'UNKNOWN'}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatFileSize(upload.fileSize || 0)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={normalizeStatus(upload.status || 'unknown').label}
                      color={normalizeStatus(upload.status || 'unknown').color as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2">
                        Total: {upload.totalWebsites || 0}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Processed: {upload.processedWebsites || 0} | Failed: {upload.failedWebsites || 0}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {upload.createdAt ? formatDate(upload.createdAt) : 'N/A'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" gap={1}>
                      <Tooltip title="View Results">
                        <IconButton
                          size="small"
                          onClick={() => handleViewResults(upload.id)}
                          color="primary"
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {pagination.totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={3}>
          <Pagination
            count={pagination.totalPages}
            page={pagination.page}
            onChange={handlePageChange}
            color="primary"
          />
        </Box>
      )}
    </Box>
  );
}
