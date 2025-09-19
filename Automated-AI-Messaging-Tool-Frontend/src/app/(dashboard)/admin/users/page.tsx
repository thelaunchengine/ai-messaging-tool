'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Avatar,
  Stack,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  TablePagination
} from '@mui/material';
import { Search, Visibility, Block, CheckCircle, Edit, Delete, Add, FilterList, Download } from '@mui/icons-material';
import MainCard from '../../../../components/MainCard';

export default function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [actionSuccess, setActionSuccess] = useState('');
  const [addUserDialogOpen, setAddUserDialogOpen] = useState(false);
  const [editUserDialogOpen, setEditUserDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [success, setSuccess] = useState('');
  const [formErrors, setFormErrors] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Validation function
  const validateForm = () => {
    const errors = {
      name: '',
      email: '',
      password: ''
    };
    
    if (!newUser.name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (!newUser.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(newUser.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    if (!newUser.password) {
      errors.password = 'Password is required';
    } else if (newUser.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }
    
    setFormErrors(errors);
    return !Object.values(errors).some(error => error !== '');
  };

  // Fetch users from API
  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/users');
      const data = await res.json();
      if (res.ok) {
        setUsers(data.users);
      } else {
        setError(data.error || 'Failed to fetch users');
      }
    } catch (err) {
      setError('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Add user
  const handleAddUser = async (newUser) => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser)
      });
      
      const data = await res.json();
      if (res.ok) {
        setSuccess(`User ${newUser.name} added successfully!`);
        setTimeout(() => setSuccess(''), 4000);
        setAddUserDialogOpen(false);
        setNewUser({ name: '', email: '', password: '' });
        // Refresh the users list
        await fetchUsers();
      } else {
        setError(data.error || 'Failed to add user');
      }
    } catch (err) {
      setError('Failed to add user');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUserData = async (id, updatedUser) => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`/api/users/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedUser)
      });
      
      const data = await res.json();
      if (res.ok) {
        setUsers((prev) => 
          prev.map(user => 
            user.id === id ? { ...user, ...updatedUser } : user
          )
        );
        setSuccess(`User ${updatedUser.name} updated successfully!`);
        setTimeout(() => setSuccess(''), 4000);
      } else {
        setError(data.error || 'Failed to update user');
      }
    } catch (err) {
      setError('Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  // Delete user
  const handleDeleteUser = async (id) => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`/api/users/${id}`, { method: 'DELETE' });
      if (res.ok) {
        const deletedUser = users.find(u => String(u.id) === String(id));
        setUsers((prev) => prev.filter((u) => String(u.id) !== String(id)));
        setSuccess(`User ${deletedUser?.name || 'Unknown'} deleted successfully!`);
        setTimeout(() => setSuccess(''), 4000);
      } else {
        const data = await res.json();
        setError(data.error || 'Failed to delete user');
      }
    } catch (err) {
      setError('Failed to delete user');
    } finally {
      setLoading(false);
    }
  };

  const handleViewUser = (user: any) => {
    setSelectedUser(user);
    setViewDialogOpen(true);
  };

  const handleEditUser = (user: any) => {
    setEditingUser(user);
    setEditUserDialogOpen(true);
  };

  const handleNewUserChange = (field: string, value: any) => {
    setNewUser((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (formErrors[field as keyof typeof formErrors]) {
      setFormErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleEditUserChange = (field: string, value: any) => {
    console.log('handleEditUserChange:', field, value);
    setEditingUser((prev) => {
      const updated = { ...prev, [field]: value };
      console.log('Updated editingUser:', updated);
      return updated;
    });
  };

  const handleUpdateUser = async () => {
    if (!editingUser) return;
    
    console.log('handleUpdateUser called with editingUser:', editingUser);
    
    setLoading(true);
    setError('');
    
    try {
      const requestBody = { 
        name: editingUser.name,
        email: editingUser.email,
        status: editingUser.status 
      };
      
      console.log('Sending request with body:', requestBody);
      
      const res = await fetch(`/api/users/${editingUser.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      
      const data = await res.json();
      console.log('Response:', res.status, data);
      
      if (res.ok) {
        // Refresh the users list from database instead of updating local state
        await fetchUsers();
        setSuccess(`User ${editingUser.name} updated successfully!`);
        setTimeout(() => setSuccess(''), 4000);
        setEditUserDialogOpen(false);
        setEditingUser(null);
      } else {
        setError(data.error || 'Failed to update user');
      }
    } catch (err) {
      console.error('Error updating user:', err);
      setError('Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  // Export users to CSV
  const handleExportUsers = () => {
    const csvData = users.map(user => ({
      User: user.name,
      Email: user.email,
      Status: user.status,
      Lists: user.filesUploaded || 0,
      Websites: user.websitesProcessed || 0,
      Messages: user.messagesSent || 0
    }));

    const headers = ['User', 'Email', 'Status', 'Lists', 'Websites', 'Messages'];
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => 
        headers.map(header => `"${row[header]}"`).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'users_export.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredUsers = users.filter(
    (user) => user.name.toLowerCase().includes(searchTerm.toLowerCase()) || user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Pagination logic
  const paginatedUsers = filteredUsers.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
          User Management
        </Typography>
      </Box>

      {actionSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {actionSuccess}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Search and Actions */}
      <MainCard sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search users by name or email..."
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
          <Grid item xs={12} md={6}>
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button variant="outlined" startIcon={<FilterList />}>
                Filter
              </Button>
              <Button variant="contained" startIcon={<Add />} onClick={() => setAddUserDialogOpen(true)} color="primary">
                Add User
              </Button>
              <Button variant="contained" startIcon={<Download />} onClick={handleExportUsers}>
                Export
              </Button>
            </Stack>
          </Grid>
        </Grid>
      </MainCard>

      {/* Users Table */}
      <MainCard>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Lists</TableCell>
                <TableCell>Websites</TableCell>
                <TableCell>Messages</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedUsers.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <Stack direction="row" alignItems="center" spacing={2}>
                      <Avatar>{user.name.charAt(0)}</Avatar>
                      <Box>
                        <Typography variant="body2" fontWeight={500}>
                          {user.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {user.email}
                        </Typography>
                      </Box>
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.status}
                      color={user.status === 'active' ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{user.filesUploaded || 0}</TableCell>
                  <TableCell>{user.websitesProcessed || 0}</TableCell>
                  <TableCell>{user.messagesSent || 0}</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      <IconButton size="small" onClick={() => handleViewUser(user)} color="primary">
                        <Visibility />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleEditUser(user)} color="secondary">
                        <Edit />
                      </IconButton>
                      <IconButton
                        color="error"
                        onClick={() => {
                          if (window.confirm('Are you sure you want to delete this user?')) {
                            handleDeleteUser(user.id);
                          }
                        }}
                      >
                        <Delete />
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
            count={filteredUsers.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            rowsPerPageOptions={[10, 25, 50, 100]}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Box>
      </MainCard>

      {/* User Details Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>User Details</DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Stack spacing={2}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Name</Typography>
                <Typography variant="body1">{selectedUser.name}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Email</Typography>
                <Typography variant="body1">{selectedUser.email}</Typography>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Status</Typography>
                <Chip
                  label={selectedUser.status}
                  color={selectedUser.status === 'active' ? 'success' : 'error'}
                  size="small"
                />
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Last Active</Typography>
                <Typography variant="body1">{selectedUser.lastActive || 'N/A'}</Typography>
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
          <Button onClick={() => {
            setViewDialogOpen(false);
            if (selectedUser) handleEditUser(selectedUser);
          }} color="primary">
            Edit User
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add User Dialog */}
      <Dialog open={addUserDialogOpen} onClose={() => {
        setAddUserDialogOpen(false);
        setFormErrors({ name: '', email: '', password: '' });
        setError('');
        setSuccess('');
      }} maxWidth="sm" fullWidth>
        <DialogTitle>Add New User</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {error && (
              <Alert severity="error" onClose={() => setError('')}>
                {error}
              </Alert>
            )}
            {success && (
              <Alert severity="success" onClose={() => setSuccess('')}>
                {success}
              </Alert>
            )}
            <TextField
              fullWidth
              label="Name *"
              value={newUser.name}
              onChange={(e) => handleNewUserChange('name', e.target.value)}
              error={!!formErrors.name}
              helperText={formErrors.name}
            />
            <TextField
              fullWidth
              label="Email *"
              type="email"
              value={newUser.email}
              onChange={(e) => handleNewUserChange('email', e.target.value)}
              error={!!formErrors.email}
              helperText={formErrors.email}
            />
            <TextField
              fullWidth
              label="Password *"
              type="password"
              value={newUser.password}
              onChange={(e) => handleNewUserChange('password', e.target.value)}
              error={!!formErrors.password}
              helperText={formErrors.password}
            />
          </Stack>
        </DialogContent>
                  <DialogActions>
            <Button variant="outlined" onClick={() => setAddUserDialogOpen(false)}>Cancel</Button>
            <Button variant="outlined" onClick={() => {
              if (validateForm()) {
                handleAddUser(newUser);
              }
            }} color="primary" disabled={loading}>
              {loading ? <CircularProgress size={20} /> : 'Add User'}
            </Button>
          </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog open={editUserDialogOpen} onClose={() => setEditUserDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          {editingUser && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                fullWidth
                label="Name"
                value={editingUser.name}
                onChange={(e) => handleEditUserChange('name', e.target.value)}
              />
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={editingUser.email}
                disabled
                sx={{ 
                  '& .MuiInputBase-input.Mui-disabled': {
                    WebkitTextFillColor: 'rgba(0, 0, 0, 0.87)',
                    backgroundColor: 'rgba(0, 0, 0, 0.04)'
                  }
                }}
              />
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={editingUser.status}
                  onChange={(e) => handleEditUserChange('status', e.target.value)}
                  label="Status"
                >
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="disabled">Disabled</MenuItem>
                </Select>
              </FormControl>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditUserDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUpdateUser} color="primary" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Update User'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
