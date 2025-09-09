'use client';

import { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Stack,
  Typography,
  Paper,
  Divider,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import MainCard from '../../../components/MainCard';

interface ContentData {
  title: string;
  content: string;
  lastUpdated?: string;
  status?: string;
}

const cookieTypes = [
  {
    name: 'Essential Cookies',
    purpose: 'Required for the website to function properly',
    duration: 'Session',
    examples: ['Authentication cookies', 'Security cookies', 'Session management']
  },
  {
    name: 'Functional Cookies',
    purpose: 'Remember your preferences and settings',
    duration: '1 year',
    examples: ['Language preferences', 'Theme settings', 'Form data']
  },
  {
    name: 'Analytics Cookies',
    purpose: 'Help us understand how visitors interact with our website',
    duration: '2 years',
    examples: ['Page views', 'Time spent on pages', 'Error tracking']
  },
  {
    name: 'Performance Cookies',
    purpose: 'Help us improve website performance',
    duration: '1 year',
    examples: ['Load balancing', 'Caching', 'CDN optimization']
  }
];

export default function CookiesPage() {
  const [content, setContent] = useState<ContentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchContent = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/content?type=cookies');

        if (response.ok) {
          const data = await response.json();
          setContent(data.content);
        } else {
          // If no content found, use default content
          setContent({
            title: 'Cookies Policy',
            content: `This Cookies Policy explains how we use cookies and similar technologies on our AI-Based Automated Messaging Tool platform.

1. What Are Cookies
Cookies are small text files that are stored on your device when you visit our website. They help us provide you with a better experience by enabling certain features and functionality.

2. How We Use Cookies
We use cookies for various purposes:
• Essential website functionality
• Remembering your preferences
• Analyzing website usage
• Improving performance
• Security and fraud prevention
• Personalizing your experience

3. Types of Cookies We Use
We use different types of cookies for different purposes. Below is a detailed breakdown of the cookies we use and their purposes.

4. Managing Cookies
You can control and manage cookies in your browser settings. However, please note that disabling certain cookies may affect the functionality of our website.

To manage cookies in your browser:
• Chrome: Settings > Privacy and security > Cookies and other site data
• Firefox: Options > Privacy & Security > Cookies and Site Data
• Safari: Preferences > Privacy > Cookies and website data
• Edge: Settings > Cookies and site permissions > Cookies

5. Third-Party Cookies
Some cookies are placed by third-party services that appear on our pages. These third parties may use cookies to:
• Analyze website usage
• Provide social media features
• Deliver targeted advertising
• Monitor performance

We recommend reviewing the privacy policies of these third-party services for more information.

6. Updates to This Policy
We may update this Cookie Policy from time to time. Any changes will be posted on this page with an updated revision date.`,
            lastUpdated: new Date().toLocaleDateString(),
            status: 'published'
          });
        }
      } catch (err) {
        setError('Failed to load content. Please try again later.');
        // Set default content on error
        setContent({
          title: 'Cookies Policy',
          content: `This Cookies Policy explains how we use cookies and similar technologies on our AI-Based Automated Messaging Tool platform.

1. What Are Cookies
Cookies are small text files that are stored on your device when you visit our website. They help us provide you with a better experience by enabling certain features and functionality.

2. How We Use Cookies
We use cookies for various purposes:
• Essential website functionality
• Remembering your preferences
• Analyzing website usage
• Improving performance
• Security and fraud prevention
• Personalizing your experience

3. Types of Cookies We Use
We use different types of cookies for different purposes. Below is a detailed breakdown of the cookies we use and their purposes.

4. Managing Cookies
You can control and manage cookies in your browser settings. However, please note that disabling certain cookies may affect the functionality of our website.

To manage cookies in your browser:
• Chrome: Settings > Privacy and security > Cookies and other site data
• Firefox: Options > Privacy & Security > Cookies and Site Data
• Safari: Preferences > Privacy > Cookies and website data
• Edge: Settings > Cookies and site permissions > Cookies

5. Third-Party Cookies
Some cookies are placed by third-party services that appear on our pages. These third parties may use cookies to:
• Analyze website usage
• Provide social media features
• Deliver targeted advertising
• Monitor performance

We recommend reviewing the privacy policies of these third-party services for more information.

6. Updates to This Policy
We may update this Cookie Policy from time to time. Any changes will be posted on this page with an updated revision date.`,
          lastUpdated: new Date().toLocaleDateString(),
          status: 'published'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && !content) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h4" fontWeight={700} sx={{ color: '#23272E' }}>
              Cookies Policy
            </Typography>
          </Box>
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
              {content?.content || 'Content not available.'}
            </Typography>
          </Paper>

          <Box>
            <Typography variant="h3" gutterBottom>
              Types of Cookies We Use
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Purpose</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>Examples</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {cookieTypes.map((type, index) => (
                    <TableRow key={index}>
                      <TableCell>{type.name}</TableCell>
                      <TableCell>{type.purpose}</TableCell>
                      <TableCell>{type.duration}</TableCell>
                      <TableCell>
                        <List dense>
                          {type.examples.map((example, i) => (
                            <ListItem key={i} disablePadding>
                              <ListItemText primary={example} />
                            </ListItem>
                          ))}
                        </List>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>

          <Box sx={{ mt: 4, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary">
              By continuing to use our Platform, you consent to the use of cookies as described in this policy. If you do not agree to
              our use of cookies, please adjust your browser settings accordingly.
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
