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
  Avatar,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Alert,
  CircularProgress,
  TablePagination,
  Card,
  CardContent
} from '@mui/material';
import {
  Search,
  Download,
  Visibility,
  History,
  CloudUpload,
  CheckCircle,
  ErrorOutline,
  Schedule,
  Person,
  FileDownload,
  FilterList
} from '@mui/icons-material';
import MainCard from '../../../../components/MainCard';

interface HistoryItem {
  id: string;
  fileName: string;
  userName: string;
  userEmail: string;
  fileSize: string;
  fileType: string;
  uploadDate: string;
  status: string;
  websitesCount: number;
  messagesSent: number;
  processedWebsites: number;
  failedWebsites: number;
  successRate: number;
  processingTime: string;
}

export default function AdminHistoryPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [userFilter, setUserFilter] = useState('all');
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [userFilesDialog, setUserFilesDialog] = useState(false);
  const [historyData, setHistoryData] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    fetchHistoryData();
  }, []);

  const fetchHistoryData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/history');
      if (response.ok) {
        const data = await response.json();
        setHistoryData(data.history || []);
      } else {
        setError('Failed to fetch history data');
      }
    } catch (error) {
      console.error('Error fetching history:', error);
      setError('Failed to fetch history data');
    } finally {
      setLoading(false);
    }
  };

  const filteredData = historyData.filter(
    (item) =>
      (item.fileName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.userEmail.toLowerCase().includes(searchTerm.toLowerCase())) &&
      (statusFilter === 'all' || item.status === statusFilter) &&
      (userFilter === 'all' || item.userName === userFilter)
  );

  // Pagination calculations
  const paginatedData = filteredData.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const stats = [
    { label: 'Total Lists', value: historyData.length, icon: <CloudUpload />, color: 'primary' },
    { label: 'Processed', value: historyData.filter((f) => f.status === 'completed').length, icon: <CheckCircle />, color: 'success' },
    { label: 'Failed', value: historyData.filter((f) => f.status === 'failed').length, icon: <ErrorOutline />, color: 'error' }
  ];

  const uniqueUsers = Array.from(new Set(historyData.map((f) => f.userName)));

  const handleViewUserFiles = (user: any) => {
    setSelectedUser(user);
    setUserFilesDialog(true);
  };

  const handleDownload = async (fileId: string) => {
    try {
      const response = await fetch(`/api/admin/history/${fileId}/download`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = historyData.find(item => item.id === fileId)?.fileName || 'download';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Failed to download file');
      }
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  if (loading && !historyData.length) {
    return (
      <Box sx={{ p: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
            List History
          </Typography>
        </Box>
        <Box sx={{ textAlign: 'center', py: 10 }}>
          <CircularProgress />
          <Typography variant="h6" mt={2}>Loading History...</Typography>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
            List History
          </Typography>
        </Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={fetchHistoryData}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
          List History
        </Typography>
      </Box>

      {/* Stats Cards - More space efficient layout */}
      <Grid container spacing={2} mb={3}>
        {stats.map((stat, idx) => (
          <Grid item xs={12} sm={6} md={4} key={idx}>
            <Card sx={{ 
              height: '100%', 
              background: `linear-gradient(135deg, ${stat.color === 'primary' ? '#1976d2' : stat.color === 'success' ? '#2e7d32' : '#d32f2f'}15, ${stat.color === 'primary' ? '#1976d2' : stat.color === 'success' ? '#2e7d32' : '#d32f2f'}08)`,
              border: `1px solid ${stat.color === 'primary' ? '#1976d2' : stat.color === 'success' ? '#2e7d32' : '#d32f2f'}30`
            }}>
              <CardContent sx={{ p: 2.5, textAlign: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1.5 }}>
                  <Box sx={{ 
                    mr: 1.5, 
                    color: `${stat.color}.main`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    backgroundColor: `${stat.color === 'primary' ? '#1976d2' : stat.color === 'success' ? '#2e7d32' : '#d32f2f'}15`
                  }}>
                    {stat.icon}
                  </Box>
                  <Typography variant="h3" fontWeight={700} sx={{ fontSize: '2rem' }}>
                    {stat.value}
                  </Typography>
                </Box>
                <Typography variant="subtitle1" color="text.secondary" fontWeight={500}>
                  {stat.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Filters */}
      <MainCard sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search files, users, or emails..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                )
              }}
              size="medium"
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="medium">
              <InputLabel>Status</InputLabel>
              <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} label="Status">
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="completed">Processed</MenuItem>
                <MenuItem value="processing">Processing</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="medium">
              <InputLabel>User</InputLabel>
              <Select value={userFilter} onChange={(e) => setUserFilter(e.target.value)} label="User">
                <MenuItem value="all">All Users</MenuItem>
                {uniqueUsers.map((user) => (
                  <MenuItem key={user} value={user}>
                    {user}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <Stack direction="row" spacing={1} sx={{ height: '56px', alignItems: 'center' }}>
              <Button 
                variant="outlined" 
                startIcon={<FilterList />} 
                fullWidth
                size="medium"
                sx={{ height: '40px' }}
              >
                Apply Filters
              </Button>
              <Button 
                variant="outlined" 
                startIcon={<Download />}
                size="medium"
                sx={{ height: '40px' }}
              >
                Export History
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </MainCard>

      {/* File History Table */}
      <MainCard title="List Upload History">
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>File</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Upload Date</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Websites</TableCell>
                <TableCell>Messages Sent</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedData.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600}>
                        {row.fileName}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {row.fileSize} • {row.fileType}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar sx={{ mr: 2, width: 32, height: 32 }}>{row.userName.charAt(0)}</Avatar>
                      <Box>
                        <Typography variant="subtitle2" fontWeight={600}>
                          {row.userName}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {row.userEmail}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">{new Date(row.uploadDate).toLocaleDateString()}</Typography>
                    <Typography variant="caption" display="block" color="text.secondary">
                      {new Date(row.uploadDate).toLocaleTimeString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={row.status}
                      color={row.status === 'completed' ? 'success' : row.status === 'processing' ? 'warning' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{row.websitesCount}</TableCell>
                  <TableCell>{row.messagesSent}</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      <IconButton size="small" onClick={() => handleDownload(row.id)} color="secondary">
                        <FileDownload />
                      </IconButton>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        {/* Pagination */}
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Results per page:"
          labelDisplayedRows={({ from, to, count }) => `${from}-${to} of ${count !== -1 ? count : `more than ${to}`}`}
        />
      </MainCard>

      {/* User Files Dialog */}
      <Dialog open={userFilesDialog} onClose={() => setUserFilesDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>File History: {selectedUser?.userName}</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" color="text.secondary">
              {selectedUser?.userEmail}
            </Typography>
          </Box>

          <List>
            {historyData.filter(item => item.userName === selectedUser?.userName).map((file) => (
              <ListItem key={file.id} divider>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: file.status === 'completed' ? 'success.main' : 'warning.main' }}>
                    <CloudUpload />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={file.fileName}
                  secondary={
                    <Box>
                      <Typography variant="caption" display="block">
                        Uploaded: {new Date(file.uploadDate).toLocaleDateString()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {file.websitesCount} websites • {file.messagesSent} messages sent
                      </Typography>
                    </Box>
                  }
                />
                <Chip label={file.status} color={file.status === 'completed' ? 'success' : 'warning'} size="small" />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUserFilesDialog(false)}>Close</Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={() => {
              console.log(`Exporting files for ${selectedUser?.userName}...`);
              setUserFilesDialog(false);
            }}
          >
            Export User Files
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
