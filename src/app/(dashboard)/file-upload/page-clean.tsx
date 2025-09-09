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
import SafeLinearProgress from './SafeLinearProgress';
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
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import CircularProgress from '@mui/material/CircularProgress';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import PreviewIcon from '@mui/icons-material/Preview';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import { MainCard } from '../../../components/MainCard';
import { AIMessageGenerationTrigger } from '../../../components/AIMessageGenerationTrigger';
import { RealTimeProgress } from '../../../components/RealTimeProgress';

// ... existing code ...

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
  const [currentFileUploadId, setCurrentFileUploadId] = useState<string | null>(null);

  // ... existing code ...

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" gutterBottom>
        Upload Website List
      </Typography>

      {/* File Upload Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Select File
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: 'grey.300',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                '&:hover': {
                  borderColor: 'primary.main',
                },
              }}
            >
              <input {...getInputProps()} />
              <UploadFileIcon sx={{ fontSize: 48, color: 'grey.500', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Drag & drop a file here, or click to select
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Supports CSV, XLSX, XLS files
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Stack spacing={2}>
              <Typography variant="subtitle1">
                File Requirements:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Must contain a "websiteUrl" column
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Optional: "contactFormUrl" column
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Maximum file size: 10MB
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Supported formats: CSV, XLSX, XLS
              </Typography>
            </Stack>
          </Grid>
        </Grid>

        {selectedFile && (
          <Box sx={{ mt: 3 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Selected file: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </Alert>
            
            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={uploading}
                startIcon={uploading ? <CircularProgress size={20} /> : <UploadFileIcon />}
              >
                {uploading ? 'Uploading...' : 'Upload File'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={() => setSelectedFile(null)}
                disabled={uploading}
              >
                Clear Selection
              </Button>
            </Stack>
          </Box>
        )}
      </Paper>

      {/* Upload Progress */}
      {uploading && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Upload Progress
          </Typography>
          <SafeLinearProgress value={uploadProgress} />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {uploadProgress.toFixed(1)}% complete
          </Typography>
        </Paper>
      )}

      {/* Upload Result */}
      {uploadResult && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            {uploadResult.status === 'COMPLETED' ? (
              <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
            ) : uploadResult.status === 'FAILED' ? (
              <ErrorIcon sx={{ color: 'error.main', mr: 1 }} />
            ) : (
              <CircularProgress size={20} sx={{ mr: 1 }} />
            )}
            <Typography variant="h6">
              Upload {uploadResult.status === 'COMPLETED' ? 'Completed' : uploadResult.status === 'FAILED' ? 'Failed' : 'Processing'}
            </Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                Total Websites
              </Typography>
              <Typography variant="h6">
                {uploadResult.totalWebsites || 0}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                Status
              </Typography>
              <Chip
                label={uploadResult.status}
                color={
                  uploadResult.status === 'COMPLETED' ? 'success' :
                  uploadResult.status === 'FAILED' ? 'error' : 'warning'
                }
                size="small"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                File ID
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                {uploadResult.fileUploadId}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                Uploaded At
              </Typography>
              <Typography variant="body2">
                {new Date(uploadResult.uploadedAt).toLocaleString()}
              </Typography>
            </Grid>
          </Grid>

          <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
            <Button
              variant="outlined"
              onClick={() => setShowPreview(true)}
              startIcon={<PreviewIcon />}
            >
              Preview Data
            </Button>
            
            <Button
              variant="outlined"
              onClick={() => router.push('/history')}
              startIcon={<DownloadIcon />}
            >
              View History
            </Button>
            
            <Button
              variant="outlined"
              color="error"
              onClick={handleCancelProcessing}
              disabled={uploadResult.status !== 'PROCESSING'}
              startIcon={<DeleteIcon />}
            >
              Cancel Processing
            </Button>
          </Stack>
        </Paper>
      )}

      {/* Data Preview Dialog */}
      <Dialog
        open={showPreview}
        onClose={() => setShowPreview(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Data Preview
          <IconButton
            onClick={() => setShowPreview(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <DeleteIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {previewData.length > 0 ? (
            <TableContainer>
              <Table>
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
