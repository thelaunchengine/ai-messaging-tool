'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Card,
  CardContent,
  InputAdornment,
  CircularProgress,
  TablePagination
} from '@mui/material';
import {
  Search,
  Download,
  FilterList,
  Analytics,
  TrendingUp,
  TrendingDown,
  FileDownload,
  People,
  CloudUpload,
  CheckCircle,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import Link from 'next/link';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import MainCard from '../../../../components/MainCard';

export default function AdminReportsPage() {
  const [reportData, setReportData] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [userReportFilter, setUserReportFilter] = useState('all');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    const fetchReportData = async () => {
      try {
        setLoading(true);
        
        // Get admin user data from localStorage
        const adminUser = localStorage.getItem('adminUser');
        if (!adminUser) {
          throw new Error('Admin user not found. Please login again.');
        }
        
        const user = JSON.parse(adminUser);
        const userId = user.id;
        
        const response = await fetch(`/api/admin/reports?userId=${userId}&t=${Date.now()}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch report data');
        }
        
        const data = await response.json();
        setReportData(data.reports || []);
        setStatistics(data.statistics || null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchReportData();
  }, []);

  const handleExport = (type: string) => {
    let dataToExport = reportData;
    let filename = 'reports_export.csv';

    if (type === 'user') {
      dataToExport = reportData.map(item => ({
        'User Name': item.userName,
        'Email': item.userEmail,
        'Files Uploaded': item.filesUploaded,
        'Websites Processed': item.websitesProcessed,
        'Messages Sent': item.messagesSent,
        'Last Activity': item.lastActivity
      }));
      filename = 'user_reports.csv';
    } else if (type === 'files') {
      dataToExport = reportData.map(item => ({
        'File Name': item.fileName || 'N/A',
        'User': item.userName,
        'Status': item.status,
        'Websites': item.websitesProcessed,
        'Messages': item.messagesSent,
        'Upload Date': item.uploadDate || 'N/A'
      }));
      filename = 'files_reports.csv';
    }

    const headers = Object.keys(dataToExport[0] || {});
    const csvContent = [
      headers.join(','),
      ...dataToExport.map(row => 
        headers.map(header => `"${row[header]}"`).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadUserReport = async (userId: string, userName: string) => {
    try {
      // Get admin user data from localStorage
      const adminUser = localStorage.getItem('adminUser');
      if (!adminUser) {
        console.error('Admin user not found. Please login again.');
        return;
      }
      
      const user = JSON.parse(adminUser);
      const adminUserId = user.id;
      
      const response = await fetch(`/api/admin/reports/user/${userId}/download?adminUserId=${adminUserId}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${userName}_processed_reports.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Failed to download user report');
      }
    } catch (error) {
      console.error('Error downloading user report:', error);
    }
  };

  const filteredData = reportData.filter(item => {
    const matchesSearch = item.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.userEmail.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  // Pagination logic
  const paginatedData = filteredData.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const stats = [
    { label: 'Total Users', value: statistics?.totalUsers || reportData.length, icon: <People />, color: 'primary' },
    { label: 'Total Files', value: statistics?.totalFiles || reportData.reduce((sum, item) => sum + (item.filesUploaded || 0), 0), icon: <CloudUpload />, color: 'secondary' },
    { label: 'Total Websites', value: statistics?.totalWebsites || reportData.reduce((sum, item) => sum + (item.websitesProcessed || 0), 0), icon: <CheckCircle />, color: 'success' },
    { label: 'Total Messages', value: statistics?.totalMessagesSent || reportData.reduce((sum, item) => sum + (item.messagesSent || 0), 0), icon: <Analytics />, color: 'info' }
  ];

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error" variant="h6">
          {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
          Reports & Analytics
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={3}>
        {stats.map((stat, idx) => (
          <Grid item xs={12} sm={6} md={3} key={idx}>
            <MainCard sx={{ p: 2, textAlign: 'center' }}>
              <Box sx={{ mb: 1, display: 'flex', justifyContent: 'center' }}>
                {stat.icon}
              </Box>
              <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
                {stat.value}
              </Typography>
              <Typography variant="subtitle2" sx={{ color: '#23272E' }}>
                {stat.label}
              </Typography>
            </MainCard>
          </Grid>
        ))}
      </Grid>

      {/* Search and Filters */}
      <MainCard sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                )
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Filter User Report</InputLabel>
              <Select
                value={userReportFilter}
                onChange={(e) => setUserReportFilter(e.target.value)}
                label="Filter User Report"
              >
                <MenuItem value="all">All Reports</MenuItem>
                <MenuItem value="active">Active Users</MenuItem>
                <MenuItem value="inactive">Inactive Users</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button variant="contained" startIcon={<Download />} onClick={() => handleExport('user')}>
                Export User Report
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </MainCard>

      {/* Detailed User Report */}
      <MainCard>
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" fontWeight={600}>
            Detailed User Report
          </Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User & Email</TableCell>
                <TableCell>Files Uploaded</TableCell>
                <TableCell>Websites Processed</TableCell>
                <TableCell>Messages Sent</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedData.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <Box>
                      <Link href={`/admin/users/${item.id}`} style={{ textDecoration: 'none' }}>
                        <Typography 
                          variant="subtitle2" 
                          fontWeight={600}
                          sx={{ 
                            color: 'primary.main',
                            cursor: 'pointer',
                            '&:hover': {
                              textDecoration: 'underline'
                            }
                          }}
                        >
                          {item.userName}
                        </Typography>
                      </Link>
                      <Typography variant="body2" color="text.secondary">
                        {item.userEmail}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{item.filesUploaded || 0}</TableCell>
                  <TableCell>{item.websitesProcessed || 0}</TableCell>
                  <TableCell>{item.messagesSent || 0}</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      <IconButton 
                        size="small" 
                        color="primary"
                        component={Link}
                        href={`/admin/users/${item.id}`}
                        title="View user uploads"
                      >
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton 
                        size="small" 
                        color="secondary"
                        onClick={() => handleDownloadUserReport(item.id, item.userName)}
                        title="Download user processed reports"
                      >
                        <Download />
                      </IconButton>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        {/* Pagination */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 2 }}>
          <TablePagination
            component="div"
            count={filteredData.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            rowsPerPageOptions={[10, 25, 50, 100]}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Box>
      </MainCard>
    </Box>
  );
}
