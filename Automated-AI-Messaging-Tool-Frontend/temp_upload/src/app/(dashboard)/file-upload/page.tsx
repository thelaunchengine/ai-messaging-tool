'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import * as XLSX from 'xlsx';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Alert from '@mui/material/Alert';
import IconButton from '@mui/material/IconButton';
import LinearProgress from '@mui/material/LinearProgress';
import Chip from '@mui/material/Chip';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CircularProgress from '@mui/material/CircularProgress';
import {
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  Refresh as RefreshIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import MainCard from '../../../components/MainCard';

interface WebsiteData {
  websiteUrl: string;
  contactFormUrl?: string;
  hasContactForm: boolean;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
}

interface UploadResult {
  id: string;
  filename: string;
  totalWebsites: number;
  processedWebsites: number;
  failedWebsites: number;
  totalChunks: number;
  completedChunks: number;
  status: string;
  createdAt: string;
  websites: WebsiteData[];
  processingInfo?: {
    estimatedTime: string;
    chunkSize: number;
    totalChunks: number;
  };
}

interface ChunkProgress {
  chunkNumber: number;
  status: string;
  processedRecords: number;
  totalRecords: number;
}

const FileUploadPage = () => {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [showTemplate, setShowTemplate] = useState(false);
  const [processingProgress, setProcessingProgress] = useState<any>(null);
  const [isTrackingProgress, setIsTrackingProgress] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file type
      const validTypes = ['.csv', '.xlsx', '.xls'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

      if (!validTypes.includes(fileExtension)) {
        setError('Please upload a CSV or Excel file (.csv, .xlsx, .xls)');
        return;
      }

      // Validate file size (100MB limit for large files)
      if (file.size > 100 * 1024 * 1024) {
        setError('File size must be less than 100MB');
        return;
      }

      setSelectedFile(file);
      setError(null);
      setUploadResult(null);
      setProcessingProgress(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    multiple: false
  });

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      // Simulate file reading and processing
      const reader = new FileReader();
      reader.onload = async (e) => {
        const content = e.target?.result as string;

        // Simulate processing progress
        const progressInterval = setInterval(() => {
          setUploadProgress((prev) => {
            if (prev >= 90) {
              clearInterval(progressInterval);
              return 90;
            }
            return prev + 10;
          });
        }, 200);

        // Prepare upload data
        const uploadData = {
          filename: selectedFile.name,
          originalName: selectedFile.name,
          fileSize: selectedFile.size,
          fileType: selectedFile.name.endsWith('.csv') ? 'csv' : 'xlsx',
          content: btoa(content) // Base64 encode
        };

        // Upload to API
        const response = await fetch('/api/upload', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(uploadData)
        });

        clearInterval(progressInterval);
        setUploadProgress(100);

        if (response.ok) {
          const result = await response.json();
          setUploadResult({
            id: result.fileUpload.id,
            filename: selectedFile.name,
            totalWebsites: result.fileUpload.totalWebsites,
            processedWebsites: 0,
            failedWebsites: 0,
            totalChunks: result.fileUpload.totalChunks,
            completedChunks: 0,
            status: result.fileUpload.status,
            createdAt: new Date().toISOString(),
            websites: [],
            processingInfo: result.processingInfo
          });
          setSelectedFile(null);

          // Start tracking progress for large files
          if (result.fileUpload.totalChunks > 1) {
            setIsTrackingProgress(true);
            startProgressTracking(result.fileUpload.id);
          }
        } else {
          const errorData = await response.json();
          setError(errorData.error || 'Upload failed');
        }
      };

      reader.readAsText(selectedFile);
    } catch (err) {
      setError('Failed to process file');
    } finally {
      setUploading(false);
    }
  };

  const startProgressTracking = async (fileUploadId: string) => {
    const trackProgress = async () => {
      try {
        const response = await fetch(`/api/upload?fileUploadId=${fileUploadId}`, {
          credentials: 'include'
        });
        if (response.ok) {
          const data = await response.json();
          setProcessingProgress(data.fileUpload);

          // Stop tracking if processing is complete
          if (data.fileUpload.status === 'COMPLETED' || data.fileUpload.status === 'FAILED') {
            setIsTrackingProgress(false);
            return;
          }
        }
      } catch (error) {
        console.error('Error tracking progress:', error);
      }

      // Continue tracking every 5 seconds
      setTimeout(trackProgress, 5000);
    };

    trackProgress();
  };

  const handlePreview = () => {
    if (!selectedFile) return;

    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const previewData: any[] = [];
        let headers: string[] = [];

        if (selectedFile.name.toLowerCase().endsWith('.csv')) {
          // Parse CSV content with proper handling of quoted values
          const lines = content.split('\n');
          if (lines.length > 0) {
            // Parse headers
            headers = parseCSVLine(lines[0]);

            // Parse first 10 data rows (skip header)
            for (let i = 1; i < Math.min(11, lines.length); i++) {
              if (lines[i]?.trim()) {
                const values = parseCSVLine(lines[i]);
                const row: any = {};
                headers.forEach((header, index) => {
                  row[header] = values[index] || '';
                });
                previewData.push(row);
              }
            }
          }
        } else if (selectedFile.name.toLowerCase().endsWith('.xlsx') || selectedFile.name.toLowerCase().endsWith('.xls')) {
          // For Excel files, we need to read as ArrayBuffer
          const arrayBuffer = e.target?.result as ArrayBuffer;
          const workbook = XLSX.read(arrayBuffer, { type: 'array' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];

          // Convert to JSON with headers
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

          if (jsonData.length > 0) {
            // First row is headers
            headers = jsonData[0] as string[];

            // Parse first 10 data rows (skip header)
            for (let i = 1; i < Math.min(11, jsonData.length); i++) {
              const rowData = jsonData[i] as any[];
              const row: any = {};
              headers.forEach((header, index) => {
                row[header] = rowData[index] || '';
              });
              previewData.push(row);
            }
          }
        }

        setPreviewData(previewData);
        setShowPreview(true);
        setError(null);
      } catch (error) {
        console.error('Error reading file:', error);
        setError('Error reading file content. Please try again.');
      }
    };

    reader.onerror = () => {
      setError('Error reading file. Please try again.');
    };

    if (selectedFile.name.toLowerCase().endsWith('.csv')) {
      reader.readAsText(selectedFile);
    } else {
      reader.readAsArrayBuffer(selectedFile);
    }
  };

  // Helper function to parse CSV line with proper handling of quoted values
  const parseCSVLine = (line: string): string[] => {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];

      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          // Escaped quote
          current += '"';
          i++; // Skip next quote
        } else {
          // Toggle quote state
          inQuotes = !inQuotes;
        }
      } else if (char === ',' && !inQuotes) {
        // End of field
        result.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }

    // Add the last field
    result.push(current.trim());
    return result;
  };

  const downloadTemplate = () => {
    const csvContent = `Website URL,Contact Form URL
https://example.com,https://example.com/contact
https://another-site.com,https://another-site.com/contact-us
https://third-site.com,`;

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'website_list_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const cancelProcessing = async () => {
    if (!uploadResult) return;

    try {
      const response = await fetch(`/api/upload/${uploadResult.id}`, {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        setUploadResult((prev) => (prev ? { ...prev, status: 'CANCELLED' } : null));
        setIsTrackingProgress(false);
      }
    } catch (error) {
      console.error('Error cancelling processing:', error);
    }
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" gutterBottom>
        Upload Website List
      </Typography>

      <Grid container spacing={3}>
        {/* File Requirements */}
        <Grid item xs={12}>
          <MainCard title="File Requirements">
            <Stack spacing={2}>
              <Typography variant="body1">Please upload a CSV or Excel file containing:</Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="Website URLs (required)" secondary="The main website URL to analyze" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Contact Form URLs (optional)" secondary="Direct link to the contact form if available" />
                </ListItem>
              </List>

              <Stack direction="row" spacing={2} alignItems="center">
                <Typography variant="body2" color="text.secondary">
                  Supported formats: .csv, .xlsx, .xls (Max 100MB)
                </Typography>
                <Button startIcon={<DownloadIcon />} onClick={downloadTemplate} size="small" variant="outlined">
                  Download Template
                </Button>
              </Stack>
            </Stack>
          </MainCard>
        </Grid>

        {/* Upload Area */}
        <Grid item xs={12}>
          <MainCard>
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'divider',
                borderRadius: 1,
                p: 3,
                textAlign: 'center',
                cursor: 'pointer',
                bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                '&:hover': {
                  bgcolor: 'action.hover'
                }
              }}
            >
              <input {...getInputProps()} />
              <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {isDragActive ? 'Drop the list here' : 'Drag & drop a list here, or click to select'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Only CSV and Excel files are supported
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}

            {selectedFile && (
              <Stack spacing={2} sx={{ mt: 2 }}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <CheckCircleIcon color="success" />
                    <Typography variant="body1">{selectedFile.name}</Typography>
                    <Chip label={`${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`} size="small" variant="outlined" />
                  </Stack>
                </Paper>

                <Stack direction="row" spacing={2}>
                  <Button variant="outlined" startIcon={<VisibilityIcon />} onClick={handlePreview}>
                    Preview Data
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleFileUpload}
                    disabled={uploading}
                    startIcon={uploading ? null : <CloudUploadIcon />}
                  >
                    {uploading ? 'Uploading...' : 'Upload & Process'}
                  </Button>
                </Stack>

                {uploading && (
                  <Box sx={{ width: '100%' }}>
                    <LinearProgress variant="determinate" value={uploadProgress} />
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Processing file... {uploadProgress}%
                    </Typography>
                  </Box>
                )}
              </Stack>
            )}
          </MainCard>
        </Grid>

        {/* Upload Result */}
        {uploadResult && (
          <Grid item xs={12}>
            <MainCard title="Upload Result">
              <Stack spacing={2}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <CheckCircleIcon color="success" />
                    <Typography variant="h6">List uploaded successfully!</Typography>
                  </Stack>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    File: {uploadResult.filename}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Processing will continue in the background.
                  </Typography>
                </Paper>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={3}>
                    <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {uploadResult.totalWebsites.toLocaleString()}
                      </Typography>
                      <Typography variant="body2">Total Websites</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="success.main">
                        {uploadResult.processedWebsites.toLocaleString()}
                      </Typography>
                      <Typography variant="body2">Processed</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="error.main">
                        {uploadResult.failedWebsites.toLocaleString()}
                      </Typography>
                      <Typography variant="body2">Failed</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={3}>
                    <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="info.main">
                        {uploadResult.totalChunks}
                      </Typography>
                      <Typography variant="body2">Chunks</Typography>
                    </Paper>
                  </Grid>
                </Grid>

                {uploadResult.processingInfo && (
                  <Alert severity="info" icon={<InfoIcon />}>
                    <Typography variant="body2">
                      <strong>Processing Info:</strong> {uploadResult.processingInfo.totalChunks} chunks of{' '}
                      {uploadResult.processingInfo.chunkSize.toLocaleString()} records each. Estimated time:{' '}
                      {uploadResult.processingInfo.estimatedTime}
                    </Typography>
                  </Alert>
                )}

                {uploadResult.status === 'PROCESSING' && (
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Button
                      variant="outlined"
                      startIcon={<RefreshIcon />}
                      onClick={() => startProgressTracking(uploadResult.id)}
                      disabled={isTrackingProgress}
                    >
                      {isTrackingProgress ? 'Tracking Progress...' : 'Track Progress'}
                    </Button>
                    <Button variant="outlined" color="error" startIcon={<CancelIcon />} onClick={cancelProcessing}>
                      Cancel Processing
                    </Button>
                  </Stack>
                )}

                <Stack direction="row" spacing={2} alignItems="center">
                  <Button variant="contained" color="primary" onClick={() => router.push('/history')}>
                    View History
                  </Button>

                  <Button
                    variant="outlined"
                    onClick={() => {
                      setUploadResult(null);
                      setProcessingProgress(null);
                      setIsTrackingProgress(false);
                    }}
                  >
                    Upload Another File
                  </Button>
                </Stack>
              </Stack>
            </MainCard>
          </Grid>
        )}

        {/* Processing Progress */}
        {processingProgress && (
          <Grid item xs={12}>
            <MainCard title="Processing Progress">
              <Stack spacing={2}>
                <Box sx={{ width: '100%' }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      Overall Progress: {processingProgress.completedChunks}/{processingProgress.totalChunks} chunks
                    </Typography>
                    <Typography variant="body2" color="primary">
                      {Math.round((processingProgress.completedChunks / processingProgress.totalChunks) * 100)}%
                    </Typography>
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={(processingProgress.completedChunks / processingProgress.totalChunks) * 100}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Card>
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          {processingProgress.processedWebsites?.toLocaleString() || 0}
                        </Typography>
                        <Typography variant="body2">Processed Records</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Card>
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="error.main">
                          {processingProgress.failedWebsites?.toLocaleString() || 0}
                        </Typography>
                        <Typography variant="body2">Failed Records</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Card>
                      <CardContent sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="info.main">
                          {processingProgress.status}
                        </Typography>
                        <Typography variant="body2">Status</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {processingProgress.chunks && processingProgress.chunks.length > 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Chunk Progress
                    </Typography>
                    <Grid container spacing={1}>
                      {processingProgress.chunks.map((chunk: ChunkProgress) => (
                        <Grid item xs={12} sm={6} md={4} key={chunk.chunkNumber}>
                          <Paper variant="outlined" sx={{ p: 1 }}>
                            <Stack direction="row" justifyContent="space-between" alignItems="center">
                              <Typography variant="body2">Chunk {chunk.chunkNumber}</Typography>
                              <Chip
                                label={chunk.status}
                                size="small"
                                color={
                                  chunk.status === 'COMPLETED'
                                    ? 'success'
                                    : chunk.status === 'PROCESSING'
                                      ? 'warning'
                                      : chunk.status === 'FAILED'
                                        ? 'error'
                                        : 'default'
                                }
                              />
                            </Stack>
                            {chunk.status === 'PROCESSING' && (
                              <LinearProgress
                                variant="determinate"
                                value={(chunk.processedRecords / chunk.totalRecords) * 100}
                                sx={{ mt: 1, height: 4 }}
                              />
                            )}
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}
              </Stack>
            </MainCard>
          </Grid>
        )}
      </Grid>

      {/* Preview Dialog */}
      <Dialog open={showPreview} onClose={() => setShowPreview(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          File Preview - First 10 Rows
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {selectedFile?.name} ({previewData.length} rows shown)
          </Typography>
        </DialogTitle>
        <DialogContent>
          {previewData.length > 0 ? (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    {Object.keys(previewData[0]).map((header) => (
                      <TableCell key={header} sx={{ fontWeight: 'bold' }}>
                        {header}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {previewData.map((row, index) => (
                    <TableRow key={index}>
                      {Object.values(row).map((value: any, cellIndex) => (
                        <TableCell
                          key={cellIndex}
                          sx={{
                            maxWidth: 200,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {value || '-'}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No data to preview
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPreview(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FileUploadPage;
