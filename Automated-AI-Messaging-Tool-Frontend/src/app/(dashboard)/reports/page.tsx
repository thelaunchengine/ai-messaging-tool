'use client';

import { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Stack,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { Download as DownloadIcon, FilterList as FilterIcon } from '@mui/icons-material';
import MainCard from '../../../components/MainCard';

// Mock data for report types
const reportTypes = [
  { id: 'all', label: 'All Messages' },
  { id: 'success', label: 'Successfully Sent' },
  { id: 'failed', label: 'Failed Attempts' },
  { id: 'pending', label: 'Pending Messages' }
];

// Mock data for status filters
const statusFilters = [
  { id: 'all', label: 'All Status' },
  { id: 'completed', label: 'Completed' },
  { id: 'processing', label: 'Processing' },
  { id: 'failed', label: 'Failed' }
];

const ReportsPage = () => {
  const [reportType, setReportType] = useState('all');
  const [status, setStatus] = useState('all');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleGenerateReport = () => {
    // TODO: Implement report generation logic
    console.log('Generating report with filters:', {
      reportType,
      status,
      startDate,
      endDate,
      searchQuery
    });
  };

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Report Generation</Typography>
        <Button variant="contained" color="primary" startIcon={<DownloadIcon />} onClick={handleGenerateReport}>
          Generate Report
        </Button>
      </Stack>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <MainCard title="Report Filters">
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Report Type</InputLabel>
                  <Select value={reportType} label="Report Type" onChange={(e) => setReportType(e.target.value)}>
                    {reportTypes.map((type) => (
                      <MenuItem key={type.id} value={type.id}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select value={status} label="Status" onChange={(e) => setStatus(e.target.value)}>
                    {statusFilters.map((filter) => (
                      <MenuItem key={filter.id} value={filter.id}>
                        {filter.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <DatePicker
                  label="Start Date"
                  value={startDate}
                  onChange={(newValue) => setStartDate(newValue)}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <DatePicker
                  label="End Date"
                  value={endDate}
                  onChange={(newValue) => setEndDate(newValue)}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Search"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by website URL or message content..."
                />
              </Grid>
            </Grid>
          </MainCard>
        </Grid>

        <Grid item xs={12}>
          <MainCard title="Report Preview">
            <Stack spacing={2}>
              <Typography variant="body1">Report will include the following information:</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                <Chip label="Website URL" />
                <Chip label="Contact Form URL" />
                <Chip label="Message Status" />
                <Chip label="Submission Date" />
                <Chip label="Message Content" />
                <Chip label="Response Status" />
              </Stack>
              <Typography variant="body2" color="text.secondary">
                The report will be generated in Excel format (.xlsx) and will include all messages matching the selected filters.
              </Typography>
            </Stack>
          </MainCard>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ReportsPage;
