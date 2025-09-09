'use client';

import { useState } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import LinearProgress from '@mui/material/LinearProgress';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';

// project-imports
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

// assets
import { DocumentDownload, Eye, Refresh } from '@wandersonalwes/iconsax-react';

// ==============================|| PROCESSING STATUS ||============================== //

export default function ProcessingStatus() {
  const theme = useTheme();
  const [progress, setProgress] = useState(65);

  // Mock data for the table
  const results = [
    {
      website: 'example1.com',
      status: 'Completed',
      message: 'Message sent successfully',
      timestamp: '2024-03-20 10:30:45'
    },
    {
      website: 'example2.com',
      status: 'Failed',
      message: 'Contact form not found',
      timestamp: '2024-03-20 10:31:12'
    },
    {
      website: 'example3.com',
      status: 'Processing',
      message: 'Analyzing website content',
      timestamp: '2024-03-20 10:31:45'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'processing':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Grid container spacing={GRID_COMMON_SPACING}>
      <Grid size={12}>
        <MainCard title="Processing Status">
          <Stack spacing={3}>
            <Stack spacing={1}>
              <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
                <Typography variant="subtitle1">Overall Progress</Typography>
                <Typography variant="subtitle1">{progress}%</Typography>
              </Stack>
              <LinearProgress variant="determinate" value={progress} />
            </Stack>

            <Grid container spacing={2}>
              <Grid size={12} md={4}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Stack spacing={1}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Total Websites
                    </Typography>
                    <Typography variant="h4">150</Typography>
                  </Stack>
                </Paper>
              </Grid>
              <Grid size={12} md={4}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Stack spacing={1}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Processed
                    </Typography>
                    <Typography variant="h4">98</Typography>
                  </Stack>
                </Paper>
              </Grid>
              <Grid size={12} md={4}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Stack spacing={1}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Remaining
                    </Typography>
                    <Typography variant="h4">52</Typography>
                  </Stack>
                </Paper>
              </Grid>
            </Grid>

            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button variant="outlined" color="secondary" startIcon={<Refresh />}>
                Refresh Status
              </Button>
              <Button variant="contained" color="primary" startIcon={<DocumentDownload />}>
                Export Results
              </Button>
            </Stack>
          </Stack>
        </MainCard>
      </Grid>

      <Grid size={12}>
        <MainCard title="Processing Results">
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Website</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Message</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.website}</TableCell>
                    <TableCell>
                      <Chip label={row.status} color={getStatusColor(row.status)} size="small" />
                    </TableCell>
                    <TableCell>{row.message}</TableCell>
                    <TableCell>{row.timestamp}</TableCell>
                    <TableCell align="right">
                      <IconButton size="small" color="primary">
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
