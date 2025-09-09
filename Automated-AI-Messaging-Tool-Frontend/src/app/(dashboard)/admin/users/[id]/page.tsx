"use client";

import { useState, useEffect } from "react";
import {
  Box,
  Chip,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Stack,
  TablePagination,
  CircularProgress,
  Alert,
  Button,
  Grid,
  Card,
  CardContent
} from "@mui/material";
import { Download as DownloadIcon, Delete as DeleteIcon, Refresh as RefreshIcon, Visibility as VisibilityIcon } from "@mui/icons-material";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

interface FileUpload {
  id: string;
  filename: string;
  originalName: string;
  uploadDate: string;
  totalWebsites: number;
  processedWebsites: number;
  failedWebsites: number;
  status: string;
  createdAt: string;
  updatedAt: string;
}

interface User {
  id: string;
  name: string;
  email: string;
  username: string;
  role: string;
  status: string;
  createdAt: string;
  totalFiles: number;
  totalWebsites: number;
  processedWebsites: number;
  failedWebsites: number;
  messagesSent: number;
  activeFiles: number;
  lastActive: string;
}

const AdminUserUploadsPage = () => {
  const { id } = useParams();
  const router = useRouter();
  const [fileUploads, setFileUploads] = useState<FileUpload[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [downloading, setDownloading] = useState<string | null>(null);

  const fetchUser = async () => {
    try {
      const response = await fetch(`/api/users/${id}`);
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        setError("Failed to fetch user details");
      }
    } catch (err) {
      setError("Error loading user details");
      console.error("Error fetching user:", err);
    }
  };

  const fetchFileUploads = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/upload?userId=${id}`);
      if (response.ok) {
        const data = await response.json();
        setFileUploads(data.fileUploads || []);
      } else {
        setError("Failed to fetch upload history");
      }
    } catch (err) {
      setError("Error loading upload history");
      console.error("Error fetching file uploads:", err);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    await Promise.all([fetchUser(), fetchFileUploads()]);
  };

  useEffect(() => {
    if (id) {
      refreshData();
    }
  }, [id]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "success";
      case "processing":
        return "warning";
      case "pending":
        return "info";
      case "failed":
        return "error";
      case "cancelled":
        return "default";
      default:
        return "default";
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const dd = String(date.getDate()).padStart(2, "0");
    const yyyy = date.getFullYear();
    return `${mm}/${dd}/${yyyy}`;
  };

  const calculateWebsiteStats = (fileUpload: any) => {
    if (!fileUpload.websites || fileUpload.websites.length === 0) {
      return { processed: 0, failed: 0 };
    }
    
    const processed = fileUpload.websites.filter((website: any) => 
      website.scrapingStatus === 'COMPLETED'
    ).length;
    
    const failed = fileUpload.websites.filter((website: any) => 
      website.scrapingStatus === 'FAILED'
    ).length;
    
    return { processed, failed };
  };

  const handleDownload = async (fileUploadId: string) => {
    try {
      setDownloading(fileUploadId);
      const response = await fetch(`/api/upload/${fileUploadId}/download`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `file_${fileUploadId}.csv`; // You can get the actual filename from the response headers
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const errorData = await response.json();
        console.error('Download failed:', errorData.error);
        setError('Failed to download file');
      }
    } catch (err) {
      console.error('Download error:', err);
      setError('Failed to download file');
    } finally {
      setDownloading(null);
    }
  };

  const handleViewResults = (fileUploadId: string) => {
    router.push(`/upload/${fileUploadId}/results`);
  };

  if (loading) {
    return (
      <Box sx={{ p: { xs: 2, md: 4 }, display: "flex", justifyContent: "center", alignItems: "center", minHeight: "400px" }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Stack direction="row" justifyContent="flex-end" alignItems="center" mb={3}>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={refreshData}>
          Refresh
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Typography variant="h5" sx={{ mb: 2 }}>
        Uploaded Lists by {user?.name || "User"}
      </Typography>

      <Paper>
        {fileUploads.length === 0 ? (
          <Box sx={{ p: 4, textAlign: "center" }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No uploaded lists found for this user
            </Typography>
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>List Name</TableCell>
                    <TableCell>Upload Date</TableCell>
                    <TableCell align="right">Total Websites</TableCell>
                    <TableCell align="right">Processed</TableCell>
                    <TableCell align="right">Failed</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {fileUploads.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                    const { processed, failed } = calculateWebsiteStats(row);
                    return (
                      <TableRow key={row.id}>
                        <TableCell>
                          <Link href={`/upload/${row.id}/results`} style={{ color: "#1976d2", textDecoration: "underline", cursor: "pointer" }}>
                            {row.originalName}
                          </Link>
                        </TableCell>
                        <TableCell>{formatDate(row.createdAt)}</TableCell>
                        <TableCell align="right">{row.totalWebsites}</TableCell>
                        <TableCell align="right">{processed}</TableCell>
                        <TableCell align="right">{failed}</TableCell>
                        <TableCell>
                          <Chip
                            label={row.status.charAt(0).toUpperCase() + row.status.slice(1).toLowerCase()}
                            color={getStatusColor(row.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            <IconButton 
                              size="small" 
                              onClick={() => handleViewResults(row.id)} 
                              title="View Results"
                              color="primary"
                            >
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                            <IconButton 
                              size="small" 
                              onClick={() => handleDownload(row.id)}
                              disabled={downloading === row.id}
                              color="secondary"
                            >
                              {downloading === row.id ? (
                                <CircularProgress size={16} />
                              ) : (
                                <DownloadIcon fontSize="small" />
                              )}
                            </IconButton>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={fileUploads.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              onRowsPerPageChange={e => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
            />
          </>
        )}
      </Paper>
    </Box>
  );
};

export default AdminUserUploadsPage; 