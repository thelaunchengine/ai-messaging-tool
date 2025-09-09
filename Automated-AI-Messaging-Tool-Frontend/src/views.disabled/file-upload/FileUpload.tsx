'use client';

import { useState } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Alert from '@mui/material/Alert';

// project-imports
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

// assets
import { DocumentUpload, Trash } from '@wandersonalwes/iconsax-react';

// ==============================|| FILE UPLOAD ||============================== //

export default function FileUpload() {
  const theme = useTheme();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any[]>([]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = event.target.files?.[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      // Mock preview data
      setPreview([
        { website: 'example1.com', contactForm: 'example1.com/contact', status: 'Pending' },
        { website: 'example2.com', contactForm: 'example2.com/contact', status: 'Pending' },
        { website: 'example3.com', contactForm: 'example3.com/contact', status: 'Pending' }
      ]);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setPreview([]);
  };

  return (
    <Grid container spacing={GRID_COMMON_SPACING}>
      <Grid size={12}>
        <MainCard title="Upload Website List">
          <Stack spacing={3}>
            <Alert severity="info">
              Please upload a CSV or Excel file containing website URLs and their corresponding Contact Form URLs. The file should have two
              columns: Website URL and Contact Form URL.
            </Alert>

            <Stack
              sx={{
                border: '1px dashed',
                borderColor: 'divider',
                borderRadius: 1,
                p: 3,
                textAlign: 'center',
                position: 'relative'
              }}
            >
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={handleFileUpload}
                style={{
                  position: 'absolute',
                  width: '100%',
                  height: '100%',
                  top: 0,
                  left: 0,
                  opacity: 0,
                  cursor: 'pointer'
                }}
              />
              <DocumentUpload style={{ fontSize: '3rem', color: theme.palette.primary.main, margin: '0 auto' }} />
              <Typography variant="h6" sx={{ mt: 2 }}>
                {file ? file.name : 'Drag & Drop or Click to Upload'}
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Supported formats: .csv, .xlsx
              </Typography>
            </Stack>

            {file && (
              <Stack direction="row" spacing={2} justifyContent="flex-end">
                <Button variant="outlined" color="error" startIcon={<Trash />} onClick={handleRemoveFile}>
                  Remove File
                </Button>
                <Button variant="contained" color="primary">
                  Process File
                </Button>
              </Stack>
            )}
          </Stack>
        </MainCard>
      </Grid>

      {preview.length > 0 && (
        <Grid size={12}>
          <MainCard title="File Preview">
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Website URL</TableCell>
                    <TableCell>Contact Form URL</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {preview.map((row, index) => (
                    <TableRow key={index}>
                      <TableCell>{row.website}</TableCell>
                      <TableCell>{row.contactForm}</TableCell>
                      <TableCell>{row.status}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </MainCard>
        </Grid>
      )}
    </Grid>
  );
}
