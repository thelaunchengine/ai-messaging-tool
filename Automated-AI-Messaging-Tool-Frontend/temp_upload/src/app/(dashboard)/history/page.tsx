'use client';

import { useState, useEffect } from 'react';
import { styled } from '@mui/material/styles';
import {
  Box,
  Button,
  Chip,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Stack,
  TablePagination,
  CircularProgress,
  Alert,
  TextField
} from '@mui/material';
import { Download as DownloadIcon, Delete as DeleteIcon, Refresh as RefreshIcon, Visibility as VisibilityIcon } from '@mui/icons-material';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import MainCard from '../../../components/MainCard';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import Link from 'next/link';

interface FileUpload {
  id: string;
  filename: string;
  originalName: string;
  uploadDate: string;
  totalWebsites: number;
  processedWebsites: number;
  failedWebsites: number;
  status: string;
  createdAt: string;
  updatedAt: string;
  chunks: {
    chunkNumber: number;
    status: string;
    processedRecords: number;
    totalRecords: number;
  }[];
}

const HistoryPage = () => {
  const { data: session, status: sessionStatus } = useSession();
  const router = useRouter();
  const [fileUploads, setFileUploads] = useState<FileUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [listName, setListName] = useState('');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [filteredFileUploads, setFilteredFileUploads] = useState<FileUpload[]>([]);

  const fetchFileUploads = async (filters = {}) => {
    try {
      setLoading(true);
      setError(null);

      const userId = session?.user?.id || '';
      let url = userId ? `/api/upload?userId=${userId}` : '/api/upload';

      // Add filters to query string if present
      const params = [];
      if (filters.listName) params.push(`listName=${encodeURIComponent(filters.listName)}`);
      if (filters.startDate) params.push(`startDate=${encodeURIComponent(filters.startDate)}`);
      if (filters.endDate) params.push(`endDate=${encodeURIComponent(filters.endDate)}`);
      if (params.length > 0) {
        url += (url.includes('?') ? '&' : '?') + params.join('&');
      }

      const response = await fetch(url, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setFileUploads(data.fileUploads || []);
      } else {
        setError('Failed to fetch upload history');
      }
    } catch (err) {
      setError('Error loading upload history');
      console.error('Error fetching file uploads:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sessionStatus === 'loading') return; // Wait for session to finish loading
    if (session?.user?.id) {
      fetchFileUploads();
    } else {
      setLoading(false);
      setError('You must be logged in to view upload history.');
    }
  }, [session, sessionStatus]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    const yyyy = date.getFullYear();
    return `${mm}/${dd}/${yyyy}`;
  };

  const handleDownload = async (fileUploadId: string) => {
    try {
      // TODO: Implement download functionality
      console.log('Downloading file:', fileUploadId);
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  const handleDelete = async (fileUploadId: string) => {
    try {
      const response = await fetch(`/api/upload/${fileUploadId}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        // Refresh the list
        fetchFileUploads();
      } else {
        setError('Failed to delete file upload');
      }
    } catch (error) {
      setError('Error deleting file upload');
      console.error('Error deleting file upload:', error);
    }
  };

  const handleViewResults = (fileUploadId: string) => {
    router.push(`/upload/${fileUploadId}/results`);
  };

  // Filtering logic
  const applyFilters = () => {
    let filtered = [...fileUploads];
    if (listName) {
      filtered = filtered.filter(row => row.originalName.toLowerCase().includes(listName.toLowerCase()));
    }
    if (startDate) {
      const start = new Date(startDate).setHours(0,0,0,0);
      filtered = filtered.filter(row => new Date(row.createdAt).getTime() >= start);
    }
    if (endDate) {
      const end = new Date(endDate).setHours(23,59,59,999);
      filtered = filtered.filter(row => new Date(row.createdAt).getTime() <= end);
    }
    setFilteredFileUploads(filtered);
    setPage(0);
  };

  // Update filteredFileUploads when fileUploads changes or filters are cleared
  useEffect(() => {
    setFilteredFileUploads(fileUploads);
  }, [fileUploads]);

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
        <Typography variant="h4">Upload History</Typography>
        <Stack direction="row" spacing={2}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => fetchFileUploads()}>
            Refresh
          </Button>

        </Stack>
      </Stack>

      {/* Filter Row */}
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mb={3} alignItems="center">
        <TextField
          label="List Name"
          value={listName}
          onChange={e => setListName(e.target.value)}
          size="small"
        />
        <DatePicker
          label="Start Date"
          value={startDate}
          onChange={setStartDate}
          slotProps={{ textField: { size: 'small' } }}
        />
        <DatePicker
          label="End Date"
          value={endDate}
          onChange={setEndDate}
          slotProps={{ textField: { size: 'small' } }}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={applyFilters}
        >
          Apply Filters
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <MainCard>
        {filteredFileUploads.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No upload history found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Upload your first file to see it here
            </Typography>
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>List Name</TableCell>
                    <TableCell>Upload Date</TableCell>
                    <TableCell align="right">Total Websites</TableCell>
                    <TableCell align="right">Processed</TableCell>
                    <TableCell align="right">Failed</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredFileUploads.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => (
                    <TableRow key={row.id}>
                      <TableCell>
                        {row.originalName}
                      </TableCell>
                      <TableCell>{formatDate(row.createdAt)}</TableCell>
                      <TableCell align="right">{row.totalWebsites}</TableCell>
                      <TableCell align="right">{row.processedWebsites}</TableCell>
                      <TableCell align="right">{row.failedWebsites}</TableCell>
                      <TableCell>
                        <Chip
                          label={row.status.charAt(0).toUpperCase() + row.status.slice(1).toLowerCase()}
                          color={getStatusColor(row.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Stack direction="row" spacing={1} justifyContent="flex-end">
                          <IconButton size="small" onClick={() => handleViewResults(row.id)} title="View Results">
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                          <IconButton size="small" onClick={() => handleDownload(row.id)}>
                            <DownloadIcon fontSize="small" />
                          </IconButton>
                          <IconButton size="small" color="error" onClick={() => handleDelete(row.id)}>
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={filteredFileUploads.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </>
        )}
      </MainCard>
    </Box>
  );
};

export default HistoryPage;
