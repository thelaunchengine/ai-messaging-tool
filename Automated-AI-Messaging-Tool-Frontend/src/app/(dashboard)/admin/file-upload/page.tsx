'use client';

import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useFormik } from 'formik';
import * as Yup from 'yup';
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
  Cancel as CancelIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Pause as PauseIcon
} from '@mui/icons-material';
import MainCard from '../../../../components/MainCard';

interface UploadResult {
  id: string;
  filename: string;
  totalWebsites: number;
  status: string;
  message: string;
}

interface BatchInfo {
  batchNumber: number;
  startIndex: number;
  endIndex: number;
  totalUrls: number;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  progress: number;
}

const AdminFileUploadPage = () => {
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
  const [currentFileUploadId, setCurrentFileUploadId] = useState<string | null>(null);
  const [batches, setBatches] = useState<BatchInfo[]>([]);
  const [scrapingEnabled, setScrapingEnabled] = useState(true);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file type
      const validTypes = ['.csv', '.xlsx', '.xls'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

      if (!validTypes.includes(fileExtension)) {
        setError(`❌ Invalid file type! Please select only CSV or Excel files (.csv, .xlsx, .xls). You selected: ${file.name}`);
        return;
      }

      // Validate file size (100MB limit for large files)
      if (file.size > 100 * 1024 * 1024) {
        setError('❌ File too large! Please select a file smaller than 100MB.');
        return;
      }

      setSelectedFile(file);
      setError(null);
      setUploadResult(null);
      setProcessingProgress(null);
      
      // Preview file data
      previewFileData(file);
    }
  }, []);

  const onDropRejected = useCallback((rejectedFiles: any[]) => {
    const file = rejectedFiles[0];
    setError(`❌ File rejected: ${file.file.name}. Please check file type and size.`);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    multiple: false
  });

  const previewFileData = async (file: File) => {
    try {
      const data = await readFileData(file);
      setPreviewData(data.slice(0, 10)); // Show first 10 rows
      setShowPreview(true);
    } catch (err) {
      console.error('Error previewing file:', err);
      setError('Failed to preview file data');
    }
  };

  const readFileData = async (file: File): Promise<any[]> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          let data: any[] = [];
          
          if (file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls')) {
            const workbook = XLSX.read(e.target?.result, { type: 'binary' });
            const sheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[sheetName];
            data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
          } else {
            // CSV file
            const text = e.target?.result as string;
            const lines = text.split('\n');
            const headers = lines[0].split(',').map((h: string) => h.trim());
            
            data = lines.slice(1).map((line: string) => {
              const values = line.split(',').map((v: string) => v.trim());
              const row: any = {};
              headers.forEach((header: string, index: number) => {
                row[header] = values[index] || '';
              });
              return row;
            });
          }
          
          resolve(data);
        } catch (err) {
          reject(err);
        }
      };
      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  const calculateBatches = (totalUrls: number) => {
    const batchSize = 10000; // 10k URLs per batch
    const totalBatches = Math.ceil(totalUrls / batchSize);
    const newBatches: BatchInfo[] = [];
    
    for (let i = 0; i < totalBatches; i++) {
      const startIndex = i * batchSize;
      const endIndex = Math.min((i + 1) * batchSize, totalUrls);
      const batchUrls = endIndex - startIndex;
      
      newBatches.push({
        batchNumber: i + 1,
        startIndex,
        endIndex,
        totalUrls: batchUrls,
        status: 'PENDING',
        progress: 0
      });
    }
    
    setBatches(newBatches);
    return newBatches;
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(0);
    setError(null);
    setUploadResult(null);
    setProcessingProgress(null);

    try {
      // Read file data
      const data = await readFileData(selectedFile);
      const totalUrls = data.length;
      
      // Calculate batches (1M-6M websites split into 10 batches of 10k each)
      const calculatedBatches = calculateBatches(totalUrls);
      
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
        content: btoa(JSON.stringify(data)), // Base64 encode
        totalUrls,
        batchSize: 10000,
        enableScraping: scrapingEnabled
      };

      // Upload to API
      const response = await fetch('/api/admin/upload', {
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
        setUploadResult(result);
        setCurrentFileUploadId(result.id);
        
        // Start tracking progress
        setIsTrackingProgress(true);
        startProgressTracking(result.id);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Upload failed');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const startProgressTracking = (fileUploadId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/admin/upload/${fileUploadId}/progress`);
        if (response.ok) {
          const progress = await response.json();
          setProcessingProgress(progress);
          
          // Update batch progress
          if (progress.batches) {
            setBatches(progress.batches);
          }
          
          if (progress.status === 'COMPLETED' || progress.status === 'FAILED') {
            clearInterval(interval);
            setIsTrackingProgress(false);
          }
        }
      } catch (err) {
        console.error('Progress tracking error:', err);
      }
    }, 5000); // Check every 5 seconds
  };

  const handleStartScraping = async (batchNumber: number) => {
    if (!currentFileUploadId) return;
    
    try {
      const response = await fetch(`/api/admin/upload/${currentFileUploadId}/batch/${batchNumber}/start-scraping`, {
        method: 'POST'
      });
      
      if (response.ok) {
        // Update batch status
        setBatches(prev => prev.map(batch => 
          batch.batchNumber === batchNumber 
            ? { ...batch, status: 'PROCESSING' }
            : batch
        ));
      }
    } catch (err) {
      console.error('Error starting scraping:', err);
    }
  };

  const handleStopScraping = async (batchNumber: number) => {
    if (!currentFileUploadId) return;
    
    try {
      const response = await fetch(`/api/admin/upload/${currentFileUploadId}/batch/${batchNumber}/stop-scraping`, {
        method: 'POST'
      });
      
      if (response.ok) {
        // Update batch status
        setBatches(prev => prev.map(batch => 
          batch.batchNumber === batchNumber 
            ? { ...batch, status: 'PENDING' }
            : batch
        ));
      }
    } catch (err) {
      console.error('Error stopping scraping:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'PROCESSING':
        return 'primary';
      case 'FAILED':
        return 'error';
      case 'PENDING':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
          Admin File Upload & Scraping
        </Typography>

      </Box>



      {/* File Upload Area */}
      <MainCard sx={{ mb: 3 }}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Upload File
          </Typography>
          
          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'divider',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: isDragActive ? 'primary.50' : 'background.paper',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: 'primary.50'
              }
            }}
          >
            <input {...getInputProps()} />
            <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive ? 'Drop the file here' : 'Drag & drop a file here, or click to select'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Supports CSV, XLSX, XLS files up to 100MB
            </Typography>
            {selectedFile && (
              <Box sx={{ mt: 2 }}>
                <Chip 
                  label={selectedFile.name} 
                  color="primary" 
                  onDelete={() => setSelectedFile(null)}
                  deleteIcon={<CancelIcon />}
                />
              </Box>
            )}
          </Box>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {selectedFile && (
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                onClick={handleFileUpload}
                disabled={uploading}
                startIcon={uploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
                fullWidth
              >
                {uploading ? 'Uploading...' : 'Upload & Process File'}
              </Button>
              
              {uploading && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress variant="determinate" value={uploadProgress} />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Upload Progress: {uploadProgress}%
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </Box>
      </MainCard>

      {/* Batch Management */}
      {batches.length > 0 && (
        <MainCard sx={{ mb: 3 }}>
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Batch Management
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Control scraping for each batch individually. Each batch contains up to 10,000 URLs.
            </Typography>
            
            <Grid container spacing={2}>
              {batches.map((batch) => (
                <Grid item xs={12} sm={6} md={4} key={batch.batchNumber}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">
                          Batch {batch.batchNumber}
                        </Typography>
                        <Chip 
                          label={batch.status} 
                          color={getStatusColor(batch.status) as any}
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        URLs: {batch.startIndex + 1} - {batch.endIndex} ({batch.totalUrls} total)
                      </Typography>
                      
                      <LinearProgress 
                        variant="determinate" 
                        value={batch.progress} 
                        sx={{ mb: 2 }}
                      />
                      
                      <Typography variant="caption" color="text.secondary">
                        Progress: {batch.progress}%
                      </Typography>
                      
                      <Box sx={{ mt: 2 }}>
                        {batch.status === 'PENDING' && (
                          <Button
                            size="small"
                            variant="contained"
                            startIcon={<PlayArrowIcon />}
                            onClick={() => handleStartScraping(batch.batchNumber)}
                            fullWidth
                          >
                            Start Scraping
                          </Button>
                        )}
                        
                        {batch.status === 'PROCESSING' && (
                          <Button
                            size="small"
                            variant="outlined"
                            color="warning"
                            startIcon={<StopIcon />}
                            onClick={() => handleStopScraping(batch.batchNumber)}
                            fullWidth
                          >
                            Stop Scraping
                          </Button>
                        )}
                        
                        {batch.status === 'COMPLETED' && (
                          <Chip 
                            label="Completed" 
                            color="success" 
                            size="small"
                            icon={<CheckCircleIcon />}
                          />
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </MainCard>
      )}

      {/* File Preview */}
      {showPreview && (
        <Dialog open={showPreview} onClose={() => setShowPreview(false)} maxWidth="lg" fullWidth>
          <DialogTitle>File Preview (First 10 rows)</DialogTitle>
          <DialogContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    {previewData[0] && Object.keys(previewData[0]).map((header) => (
                      <TableCell key={header}>{header}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {previewData.map((row, index) => (
                    <TableRow key={index}>
                      {Object.values(row).map((value: any, cellIndex) => (
                        <TableCell key={cellIndex}>{value}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowPreview(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      )}

      {/* Upload Result */}
      {uploadResult && (
        <MainCard sx={{ mb: 3 }}>
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Upload Result
            </Typography>
            <Alert severity="success">
              File uploaded successfully! File ID: {uploadResult.id}
            </Alert>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>Filename:</strong> {uploadResult.filename}
              </Typography>
              <Typography variant="body2">
                <strong>Total Websites:</strong> {uploadResult.totalWebsites}
              </Typography>
              <Typography variant="body2">
                <strong>Status:</strong> {uploadResult.status}
              </Typography>
              <Typography variant="body2">
                <strong>Message:</strong> {uploadResult.message}
              </Typography>
            </Box>
          </Box>
        </MainCard>
      )}
    </Box>
  );
};

export default AdminFileUploadPage;
