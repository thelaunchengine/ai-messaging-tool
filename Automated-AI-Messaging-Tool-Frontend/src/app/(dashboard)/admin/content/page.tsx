'use client';

import { useState, useEffect } from 'react';
import {
  Grid,
  Typography,
  TextField,
  Button,
  Tabs,
  Tab,
  Paper,
  Stack,
  Alert,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { Box } from '@mui/system';
import { Save, Edit, Preview, Description, Security, Help, Cookie, Info, CheckCircle } from '@mui/icons-material';
import MainCard from '../../../../components/MainCard';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div role="tabpanel" hidden={value !== index} id={`content-tabpanel-${index}`} aria-labelledby={`content-tab-${index}`} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function AdminContentPage() {
  const [tabValue, setTabValue] = useState(0);
  const [content, setContent] = useState<any>({});
  const [editing, setEditing] = useState<string | null>(null);
  const [previewDialog, setPreviewDialog] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const contentTypes = [
    { key: 'about', label: 'About', icon: <Info /> },
    { key: 'terms', label: 'Terms of Service', icon: <Description /> },
    { key: 'privacy', label: 'Privacy Policy', icon: <Security /> },
    { key: 'help', label: 'Help & Support', icon: <Help /> },
    { key: 'cookies', label: 'Cookies Policy', icon: <Cookie /> }
  ];

  // Initialize content state with default values
  useEffect(() => {
    const defaultContent: any = {};
    contentTypes.forEach((type) => {
      defaultContent[type.key] = {
        title: type.label,
        content: '',
        lastUpdated: '',
        status: 'draft',
        version: 1
      };
    });
    setContent(defaultContent);
  }, []);

  // Fetch content for all types on mount
  useEffect(() => {
    const fetchAllContent = async () => {
      setLoading(true);
      setError('');
      const newContent: any = {};
      try {
        for (const type of contentTypes) {
          const res = await fetch(`/api/content?type=${type.key}`);
          if (res.ok) {
            const data = await res.json();
            newContent[type.key] = {
              title: data.content.title,
              content: data.content.content,
              lastUpdated: data.content.updatedAt ? new Date(data.content.updatedAt).toLocaleDateString() : '',
              status: data.content.status?.toLowerCase() || 'draft',
              version: data.content.version
            };
          } else {
            newContent[type.key] = {
              title: type.label,
              content: '',
              lastUpdated: '',
              status: 'draft',
              version: 1
            };
          }
        }
        setContent(newContent);
      } catch (err) {
        setError('Failed to load content.');
      } finally {
        setLoading(false);
      }
    };
    fetchAllContent();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setEditing(null);
  };

  const handleEdit = (contentKey: string) => {
    setEditing(contentKey);
  };

  const handleSave = async (contentKey: string) => {
    setLoading(true);
    setError('');
    try {
      const currentContent = content[contentKey];
      if (!currentContent) {
        setError('Content not found');
        return;
      }

      const res = await fetch('/api/content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: contentKey,
          title: content[contentKey]?.title || '',
          content: content[contentKey]?.content || '',
          status: 'PUBLISHED',
          createdBy: 'admin' // TODO: use real admin user id
        })
      });
      if (res.ok) {
        const data = await res.json();
        setContent((prev: any) => ({
          ...prev,
          [contentKey]: {
            ...prev[contentKey],
            lastUpdated: new Date(data.content.updatedAt).toLocaleDateString(),
            status: data.content.status?.toLowerCase() || 'published',
            version: data.content.version
          }
        }));
        setEditing(null);
        setSaveSuccess(`${contentTypes.find((t) => t.key === contentKey)?.label} updated successfully!`);
        setTimeout(() => setSaveSuccess(''), 3000);
      } else {
        const errData = await res.json();
        setError(errData.error || 'Failed to save content.');
      }
    } catch (err) {
      setError('Failed to save content.');
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = (contentKey: string) => {
    setPreviewDialog(contentKey);
  };

  const handleContentChange = (contentKey: string, field: string, value: string) => {
    setContent((prev: any) => ({
      ...prev,
      [contentKey]: {
        ...prev[contentKey],
        [field]: value
      }
    }));
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
          Static Content Management
        </Typography>
      </Box>

      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }} icon={<CheckCircle />}>
          {saveSuccess}
        </Alert>
      )}

      <MainCard>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="content tabs">
            {contentTypes.map((type, index) => (
              <Tab
                key={type.key}
                label={
                  <Stack direction="row" spacing={1} alignItems="center">
                    {type.icon}
                    <span>{type.label}</span>
                  </Stack>
                }
                id={`content-tab-${index}`}
                aria-controls={`content-tabpanel-${index}`}
              />
            ))}
          </Tabs>
        </Box>

        {contentTypes.map((type, index) => (
          <TabPanel key={type.key} value={tabValue} index={index}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <Typography>Loading content...</Typography>
              </Box>
            ) : (
              <>
                <Box sx={{ mb: 3 }}>
                  <Stack direction="row" spacing={2} justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography variant="h6" fontWeight={600}>
                        {content[type.key]?.title || type.label}
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="center">
                        <Typography variant="caption" color="text.secondary">
                          Last updated: {content[type.key]?.lastUpdated || 'Never'}
                        </Typography>
                        <Chip label={content[type.key]?.status || 'draft'} color="success" size="small" />
                      </Stack>
                    </Box>
                    <Stack direction="row" spacing={1}>
                      <Button variant="outlined" startIcon={<Preview />} onClick={() => handlePreview(type.key)}>
                        Preview
                      </Button>
                      {editing === type.key ? (
                        <Button variant="contained" startIcon={<Save />} onClick={() => handleSave(type.key)}>
                          Save
                        </Button>
                      ) : (
                        <Button variant="outlined" startIcon={<Edit />} onClick={() => handleEdit(type.key)}>
                          Edit
                        </Button>
                      )}
                    </Stack>
                  </Stack>
                </Box>

                {editing === type.key ? (
                  <Stack spacing={3}>
                    <TextField
                      fullWidth
                      label="Title"
                      value={content[type.key]?.title || ''}
                      onChange={(e) => handleContentChange(type.key, 'title', e.target.value)}
                      variant="outlined"
                    />
                    <TextField
                      fullWidth
                      label="Content"
                      value={content[type.key]?.content || ''}
                      onChange={(e) => handleContentChange(type.key, 'content', e.target.value)}
                      variant="outlined"
                      multiline
                      rows={15}
                    />
                  </Stack>
                ) : (
                  <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
                    <Typography variant="h5" fontWeight={600} mb={2}>
                      {content[type.key]?.title || type.label}
                    </Typography>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                      {content[type.key]?.content || ''}
                    </Typography>
                  </Paper>
                )}
              </>
            )}
          </TabPanel>
        ))}
      </MainCard>

      {/* Preview Dialog */}
      <Dialog open={!!previewDialog} onClose={() => setPreviewDialog(null)} maxWidth="md" fullWidth>
        <DialogTitle>Preview: {previewDialog && content[previewDialog as keyof typeof content]?.title}</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
            {previewDialog && content[previewDialog as keyof typeof content]?.content}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialog(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
