'use client';

import { useState, useEffect } from 'react';
import { Box, Grid, Stack, Typography, Paper, Divider, CircularProgress, Alert } from '@mui/material';
import MainCard from '../../../components/MainCard';

interface ContentData {
  title: string;
  content: string;
  lastUpdated?: string;
  status?: string;
}

export default function TermsPage() {
  const [content, setContent] = useState<ContentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchContent = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/content?type=terms');

        if (response.ok) {
          const data = await response.json();
          setContent(data.content);
        } else {
          // If no content found, use default content
          setContent({
            title: 'Terms of Service',
            content: `1. Acceptance of Terms
By accessing and using the AI-Based Automated Messaging Tool ("the Platform"), you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Platform.

2. Description of Service
The Platform provides an AI-powered automation system for interacting with Contact Us forms across multiple websites. The service includes website analysis, message generation, and automated form submission capabilities.

3. User Responsibilities
Users are responsible for:
• Providing accurate and valid website URLs and contact form URLs
• Ensuring they have the right to contact the websites listed
• Maintaining the confidentiality of their account credentials
• Using the Platform in compliance with all applicable laws and regulations

4. AI Model Usage
The Platform utilizes AI models (such as ChatGPT or Gemini) for message generation. Users must:
• Provide valid API credentials for the chosen AI model
• Use the AI-generated content responsibly
• Not use the service for spam or malicious purposes

5. Data Privacy
We are committed to protecting your privacy. The Platform:
• Collects and processes data necessary for service provision
• Implements appropriate security measures
• Does not share your data with third parties without consent
• Complies with relevant data protection regulations

6. Service Limitations
The Platform:
• May have rate limits on API calls
• Cannot guarantee 100% success rate for form submissions
• May be subject to downtime for maintenance
• Reserves the right to modify or discontinue features

7. Intellectual Property
All content, features, and functionality of the Platform are owned by us and are protected by international copyright, trademark, and other intellectual property laws.

8. Termination
We reserve the right to terminate or suspend access to the Platform for violations of these terms or for any other reason at our sole discretion.

9. Disclaimer of Warranties
The Platform is provided "as is" without warranties of any kind, either express or implied. We do not guarantee that the service will be uninterrupted or error-free.

10. Limitation of Liability
We shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of or inability to use the Platform.

11. Changes to Terms
We reserve the right to modify these terms at any time. Users will be notified of significant changes. Continued use of the Platform after changes constitutes acceptance of the new terms.

12. Contact Information
For questions about these Terms of Service, please contact us at support@example.com`,
            lastUpdated: new Date().toLocaleDateString(),
            status: 'published'
          });
        }
      } catch (err) {
        setError('Failed to load content. Please try again later.');
        // Set default content on error
        setContent({
          title: 'Terms of Service',
          content: `1. Acceptance of Terms
By accessing and using the AI-Based Automated Messaging Tool ("the Platform"), you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Platform.

2. Description of Service
The Platform provides an AI-powered automation system for interacting with Contact Us forms across multiple websites. The service includes website analysis, message generation, and automated form submission capabilities.

3. User Responsibilities
Users are responsible for:
• Providing accurate and valid website URLs and contact form URLs
• Ensuring they have the right to contact the websites listed
• Maintaining the confidentiality of their account credentials
• Using the Platform in compliance with all applicable laws and regulations

4. AI Model Usage
The Platform utilizes AI models (such as ChatGPT or Gemini) for message generation. Users must:
• Provide valid API credentials for the chosen AI model
• Use the AI-generated content responsibly
• Not use the service for spam or malicious purposes

5. Data Privacy
We are committed to protecting your privacy. The Platform:
• Collects and processes data necessary for service provision
• Implements appropriate security measures
• Does not share your data with third parties without consent
• Complies with relevant data protection regulations

6. Service Limitations
The Platform:
• May have rate limits on API calls
• Cannot guarantee 100% success rate for form submissions
• May be subject to downtime for maintenance
• Reserves the right to modify or discontinue features

7. Intellectual Property
All content, features, and functionality of the Platform are owned by us and are protected by international copyright, trademark, and other intellectual property laws.

8. Termination
We reserve the right to terminate or suspend access to the Platform for violations of these terms or for any other reason at our sole discretion.

9. Disclaimer of Warranties
The Platform is provided "as is" without warranties of any kind, either express or implied. We do not guarantee that the service will be uninterrupted or error-free.

10. Limitation of Liability
We shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of or inability to use the Platform.

11. Changes to Terms
We reserve the right to modify these terms at any time. Users will be notified of significant changes. Continued use of the Platform after changes constitutes acceptance of the new terms.

12. Contact Information
For questions about these Terms of Service, please contact us at support@example.com`,
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
              Terms of Service
            </Typography>
          </Box>
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
              {content?.content || 'Content not available.'}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
