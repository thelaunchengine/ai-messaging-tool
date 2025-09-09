'use client';

import { useState } from 'react';
import {
  Grid,
  Stack,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  IconButton
} from '@mui/material';
import { useTheme } from '@mui/material';
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';
import { Refresh, Eye } from '@wandersonalwes/iconsax-react';

interface ProcessingResult {
  website: string;
  status: 'completed' | 'processing' | 'failed';
  progress: number;
  message: string;
  timestamp: string;
}

export default function ProcessingStatus() {
  const theme = useTheme();
  const [results, setResults] = useState<ProcessingResult[]>([
    {
      website: 'example1.com',
      status: 'completed',
      progress: 100,
      message: 'Message sent successfully',
      timestamp: '2024-03-20 10:30:45'
    },
    {
      website: 'example2.com',
      status: 'processing',
      progress: 45,
      message: 'Processing contact form',
      timestamp: '2024-03-20 10:31:12'
    },
    {
      website: 'example3.com',
      status: 'failed',
      progress: 0,
      message: 'Failed to access contact form',
      timestamp: '2024-03-20 10:31:45'
    }
  ]);

  const handleRefresh = () => {
    // TODO: Implement refresh logic
    console.log('Refreshing status...');
  };

  const handleViewDetails = (website: string) => {
    // TODO: Implement view details logic
    console.log('Viewing details for:', website);
  };

  const getStatusColor = (status: ProcessingResult['status']) => {
    switch (status) {
      case 'completed':
        return theme.palette.success.main;
      case 'processing':
        return theme.palette.warning.main;
      case 'failed':
        return theme.palette.error.main;
      default:
        return theme.palette.text.primary;
    }
  };

  return (
    <Grid container spacing={GRID_COMMON_SPACING}>
      <Grid xs={12}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h3">Processing Status</Typography>
          <Button variant="outlined" startIcon={<Refresh />} onClick={handleRefresh}>
            Refresh
          </Button>
        </Stack>
      </Grid>

      <Grid xs={12}>
        <MainCard title="Processing Results">
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Website</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell>Message</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((result, index) => (
                  <TableRow key={index}>
                    <TableCell>{result.website}</TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: getStatusColor(result.status) }}>
                        {result.status.charAt(0).toUpperCase() + result.status.slice(1)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Stack spacing={1}>
                        <LinearProgress
                          variant="determinate"
                          value={result.progress}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: theme.palette.grey[200],
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: getStatusColor(result.status)
                            }
                          }}
                        />
                        <Typography variant="body2" color="textSecondary">
                          {result.progress}%
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>{result.message}</TableCell>
                    <TableCell>{result.timestamp}</TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => handleViewDetails(result.website)}>
                        <Eye />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </MainCard>
      </Grid>
    </Grid>
  );
}
