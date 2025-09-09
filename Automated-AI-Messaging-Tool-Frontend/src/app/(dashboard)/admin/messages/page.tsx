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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Alert,
  Card,
  CardContent,
  Tabs,
  Tab,
  LinearProgress,
  Tooltip,
  Switch,
  FormControlLabel,
  TablePagination
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Business,
  Message,
  Category,
  Analytics,
  ContentCopy,
  Visibility,
  TrendingUp,
  CheckCircle,
  Error
} from '@mui/icons-material';
import MainCard from '../../../../components/MainCard';

interface PredefinedMessage {
  id: string;
  industry: string;
  service: string;
  message: string;
  status: 'ACTIVE' | 'INACTIVE';
  usageCount: number;
  createdBy?: string;
  createdAt: string;
  updatedAt: string;
  tags?: string[];
  messageType: 'general' | 'partnership' | 'inquiry' | 'custom';
  targetAudience?: string;
  tone?: 'professional' | 'friendly' | 'formal' | 'casual';
}

const industries = [
  'Technology',
  'Healthcare',
  'Restaurant',
  'Real Estate',
  'Education',
  'Finance',
  'Retail',
  'Manufacturing',
  'Consulting',
  'Legal',
  'Marketing',
  'Automotive',
  'Travel',
  'Fitness',
  'Beauty',
  'Home Services',
  'Other'
];

const services = [
  'Web Development',
  'Mobile Apps',
  'Medical Equipment',
  'Food Delivery',
  'Property Management',
  'Consulting',
  'Marketing',
  'Legal Services',
  'Financial Services',
  'Education',
  'Manufacturing',
  'Retail',
  'Software Development',
  'Digital Marketing',
  'SEO',
  'Content Creation',
  'Graphic Design',
  'Video Production',
  'E-commerce',
  'Other'
];

const messageTypes = [
  { value: 'general', label: 'General Inquiry' },
  { value: 'partnership', label: 'Partnership Proposal' },
  { value: 'inquiry', label: 'Service Inquiry' },
  { value: 'custom', label: 'Custom Message' }
];

const tones = [
  { value: 'professional', label: 'Professional' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'formal', label: 'Formal' },
  { value: 'casual', label: 'Casual' }
];

export default function AdminMessagesPage() {
  const [messages, setMessages] = useState<PredefinedMessage[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMessage, setSelectedMessage] = useState<PredefinedMessage | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [actionSuccess, setActionSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [filterIndustry, setFilterIndustry] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [showPreview, setShowPreview] = useState<string | null>(null);
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [newMessage, setNewMessage] = useState({
    industry: '',
    service: '',
    message: '',
    status: 'ACTIVE' as const,
    messageType: 'general' as const,
    tone: 'professional' as const,
    targetAudience: '',
    tags: [] as string[]
  });

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/predefined-messages');
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddMessage = async () => {
    if (newMessage.industry && newMessage.service && newMessage.message) {
      setLoading(true);
      try {
        const response = await fetch('/api/predefined-messages', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newMessage)
        });

        if (response.ok) {
          await fetchMessages();
          setNewMessage({
            industry: '',
            service: '',
            message: '',
            status: 'ACTIVE',
            messageType: 'general',
            tone: 'professional',
            targetAudience: '',
            tags: []
          });
          setDialogOpen(false);
          setActionSuccess('Message added successfully!');
          setTimeout(() => setActionSuccess(''), 3000);
        }
      } catch (error) {
        console.error('Error adding message:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEditMessage = async () => {
    if (selectedMessage && newMessage.industry && newMessage.service && newMessage.message) {
      setLoading(true);
      try {
        const response = await fetch(`/api/predefined-messages/${selectedMessage.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newMessage)
        });

        if (response.ok) {
          await fetchMessages();
          setSelectedMessage(null);
          setNewMessage({
            industry: '',
            service: '',
            message: '',
            status: 'ACTIVE',
            messageType: 'general',
            tone: 'professional',
            targetAudience: '',
            tags: []
          });
          setDialogOpen(false);
          setIsEditing(false);
          setActionSuccess('Message updated successfully!');
          setTimeout(() => setActionSuccess(''), 3000);
        }
      } catch (error) {
        console.error('Error updating message:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleDeleteMessage = async (messageId: string) => {
    if (confirm('Are you sure you want to delete this message?')) {
      setLoading(true);
      try {
        const response = await fetch(`/api/predefined-messages/${messageId}`, {
          method: 'DELETE'
        });

        if (response.ok) {
          await fetchMessages();
          setActionSuccess('Message deleted successfully!');
          setTimeout(() => setActionSuccess(''), 3000);
        }
      } catch (error) {
        console.error('Error deleting message:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEdit = (message: PredefinedMessage) => {
    setSelectedMessage(message);
    setNewMessage({
      industry: message.industry,
      service: message.service,
      message: message.message,
      status: message.status,
      messageType: message.messageType,
      tone: message.tone || 'professional',
      targetAudience: message.targetAudience || '',
      tags: message.tags || []
    });
    setIsEditing(true);
    setDialogOpen(true);
  };

  const handleNewMessageChange = (field: string, value: any) => {
    setNewMessage((prev) => ({ ...prev, [field]: value }));
  };

  const handleCopyMessage = (message: string) => {
    navigator.clipboard.writeText(message);
    setActionSuccess('Message copied to clipboard!');
    setTimeout(() => setActionSuccess(''), 2000);
  };

  const filteredMessages = messages.filter((msg) => {
    const matchesSearch =
      msg.industry.toLowerCase().includes(searchTerm.toLowerCase()) ||
      msg.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
      msg.message.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesIndustry = !filterIndustry || msg.industry === filterIndustry;
    const matchesStatus = !filterStatus || msg.status === filterStatus;

    return matchesSearch && matchesIndustry && matchesStatus;
  });

  // Pagination calculations
  const paginatedMessages = filteredMessages.slice(
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
    {
      label: 'Total Messages',
      value: messages.length,
      color: 'primary',
      icon: <Message />
    },
    {
      label: 'Active Messages',
      value: messages.filter((m) => m.status === 'ACTIVE').length,
      color: 'success',
      icon: <CheckCircle />
    },
    {
      label: 'Industries Covered',
      value: new Set(messages.map((m) => m.industry)).size,
      color: 'info',
      icon: <Business />
    },
    {
      label: 'Total Usage',
      value: messages.reduce((sum, m) => sum + m.usageCount, 0),
      color: 'warning',
      icon: <TrendingUp />
    }
  ];

  const topUsedMessages = messages.sort((a, b) => b.usageCount - a.usageCount).slice(0, 5);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
          Pre-Define Messages
        </Typography>
      </Box>

      {actionSuccess && (
        <Alert severity="success" sx={{ mb: 3 }} icon={<CheckCircle />}>
          {actionSuccess}
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <MainCard>
              <Stack direction="row" spacing={2} alignItems="center">
                <Box sx={{ color: `${stat.color}.main` }}>{stat.icon}</Box>
                <Box>
                  <Typography variant="h4" sx={{ color: '#23272E' }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                </Box>
              </Stack>
            </MainCard>
          </Grid>
        ))}
      </Grid>

      {/* Search and Filters */}
      <MainCard sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search messages by industry, service, or content..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search />
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth sx={{ minWidth: 180 }}>
              <InputLabel>Industry</InputLabel>
              <Select value={filterIndustry} onChange={(e) => setFilterIndustry(e.target.value)} label="Industry">
                <MenuItem value="">All Industries</MenuItem>
                {industries.map((industry) => (
                  <MenuItem key={industry} value={industry}>
                    {industry}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth sx={{ minWidth: 180 }}>
              <InputLabel>Status</InputLabel>
              <Select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} label="Status">
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="ACTIVE">Active</MenuItem>
                <MenuItem value="INACTIVE">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button
                variant="outlined"
                startIcon={<Add />}
                onClick={() => {
                  setIsEditing(false);
                  setNewMessage({
                    industry: '',
                    service: '',
                    message: '',
                    status: 'ACTIVE',
                    messageType: 'general',
                    tone: 'professional',
                    targetAudience: '',
                    tags: []
                  });
                  setDialogOpen(true);
                }}
                color="primary"
              >
                Add Message
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </MainCard>

      {/* Messages Table */}
      <MainCard>
        {loading && <LinearProgress />}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Industry</TableCell>
                <TableCell>Service</TableCell>
                <TableCell>Message Type</TableCell>
                <TableCell>Message</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedMessages.map((message) => (
                <TableRow key={message.id}>
                  <TableCell>
                    <Chip 
                      label={message.industry} 
                      color="primary" 
                      size="small" 
                      icon={<Business />} 
                      sx={{ 
                        color: 'white',
                        '& .MuiChip-icon': {
                          color: 'white !important'
                        }
                      }} 
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={message.service} 
                      color="secondary" 
                      size="small" 
                      icon={<Category />} 
                      sx={{ 
                        color: 'white',
                        '& .MuiChip-icon': {
                          color: 'white !important'
                        }
                      }} 
                    />
                  </TableCell>
                  <TableCell>
                    <Chip label={message.messageType} color="info" size="small" />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ maxWidth: 300 }}>
                      {message.message.length > 100 ? `${message.message.substring(0, 100)}...` : message.message}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={message.status} color={message.status === 'ACTIVE' ? 'success' : 'default'} size="small" />
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      <Tooltip title="Preview">
                        <IconButton size="small" onClick={() => setShowPreview(message.id)} color="info">
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => handleEdit(message)} color="primary">
                          <Edit />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" onClick={() => handleDeleteMessage(message.id)} color="error">
                          <Delete />
                        </IconButton>
                      </Tooltip>
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
          count={filteredMessages.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Results per page:"
          labelDisplayedRows={({ from, to, count }) => `${from}-${to} of ${count !== -1 ? count : `more than ${to}`}`}
        />
      </MainCard>

      {/* Add/Edit Message Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{isEditing ? 'Edit Message' : 'Add New Message'}</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Industry</InputLabel>
                  <Select value={newMessage.industry} onChange={(e) => handleNewMessageChange('industry', e.target.value)} label="Industry">
                    <MenuItem value="">DEFAULT</MenuItem>
                    {industries.map((industry) => (
                      <MenuItem key={industry} value={industry}>
                        {industry}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Service</InputLabel>
                  <Select value={newMessage.service} onChange={(e) => handleNewMessageChange('service', e.target.value)} label="Service">
                    <MenuItem value="">DEFAULT</MenuItem>
                    {services.map((service) => (
                      <MenuItem key={service} value={service}>
                        {service}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Message Type</InputLabel>
                  <Select
                    value={newMessage.messageType}
                    onChange={(e) => handleNewMessageChange('messageType', e.target.value)}
                    label="Message Type"
                  >
                    {messageTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Tone</InputLabel>
                  <Select value={newMessage.tone} onChange={(e) => handleNewMessageChange('tone', e.target.value)} label="Tone">
                    {tones.map((tone) => (
                      <MenuItem key={tone.value} value={tone.value}>
                        {tone.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <TextField
              fullWidth
              label="Target Audience"
              value={newMessage.targetAudience}
              onChange={(e) => handleNewMessageChange('targetAudience', e.target.value)}
              placeholder="e.g., Small business owners, Tech startups"
            />

            <TextField
              fullWidth
              label="Message"
              multiline
              rows={6}
              value={newMessage.message}
              onChange={(e) => handleNewMessageChange('message', e.target.value)}
              placeholder="Enter your predefined message here..."
              required
            />

            <FormControlLabel
              control={
                <Switch
                  checked={newMessage.status === 'ACTIVE'}
                  onChange={(e) => handleNewMessageChange('status', e.target.checked ? 'ACTIVE' : 'INACTIVE')}
                />
              }
              label="Active"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={isEditing ? handleEditMessage : handleAddMessage}
            disabled={!newMessage.industry || !newMessage.service || !newMessage.message || loading}
          >
            {loading ? 'Saving...' : isEditing ? 'Update Message' : 'Add Message'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog open={!!showPreview} onClose={() => setShowPreview(null)} maxWidth="md" fullWidth>
        <DialogTitle>Message Preview</DialogTitle>
        <DialogContent>
          {showPreview && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {messages.find((m) => m.id === showPreview)?.message}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPreview(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
