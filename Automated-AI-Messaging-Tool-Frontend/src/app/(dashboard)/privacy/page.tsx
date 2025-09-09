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

export default function PrivacyPage() {
  const [content, setContent] = useState<ContentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchContent = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/content?type=privacy');

        if (response.ok) {
          const data = await response.json();
          setContent(data.content);
        } else {
          // If no content found, use default content
          setContent({
            title: 'Privacy Policy',
            content: `This Privacy Policy describes how we collect, use, and protect your personal information when you use our AI-Based Automated Messaging Tool.

1. Information We Collect
We collect information you provide directly to us, such as:
• Account information (name, email, password)
• Website URLs and contact form data
• AI model API credentials
• Usage data and analytics

2. How We Use Your Information
We use the collected information to:
• Provide and maintain our services
• Process your requests and transactions
• Send you important updates and notifications
• Improve our platform and user experience
• Ensure security and prevent fraud

3. Information Sharing
We do not sell, trade, or otherwise transfer your personal information to third parties except:
• With your explicit consent
• To comply with legal obligations
• To protect our rights and safety
• With service providers who assist in our operations

4. Data Security
We implement appropriate security measures to protect your information:
• Encryption of data in transit and at rest
• Regular security audits and updates
• Access controls and authentication
• Secure data centers and infrastructure

5. Your Rights and Choices
You have the right to:
• Access your personal information
• Correct inaccurate data
• Request deletion of your data
• Export your data
• Opt-out of marketing communications
• Withdraw consent for data processing

6. Cookies and Tracking
We use cookies and similar technologies to:
• Maintain your session
• Remember your preferences
• Analyze platform usage
• Improve user experience
• Provide personalized content

7. Data Retention
We retain your data for:
• As long as your account is active
• As required by law
• As necessary to provide our services
• Until you request deletion

8. International Data Transfers
Your data may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place for such transfers in compliance with applicable data protection laws.

9. Children's Privacy
Our services are not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13.

10. Changes to Privacy Policy
We may update this privacy policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "Last Updated" date.

11. Contact Us
If you have any questions about this Privacy Policy, please contact us at:
Email: privacy@example.com
Address: [Your Company Address]
Phone: [Your Company Phone]`,
            lastUpdated: new Date().toLocaleDateString(),
            status: 'published'
          });
        }
      } catch (err) {
        setError('Failed to load content. Please try again later.');
        // Set default content on error
        setContent({
          title: 'Privacy Policy',
          content: `This Privacy Policy describes how we collect, use, and protect your personal information when you use our AI-Based Automated Messaging Tool.

1. Information We Collect
We collect information you provide directly to us, such as:
• Account information (name, email, password)
• Website URLs and contact form data
• AI model API credentials
• Usage data and analytics

2. How We Use Your Information
We use the collected information to:
• Provide and maintain our services
• Process your requests and transactions
• Send you important updates and notifications
• Improve our platform and user experience
• Ensure security and prevent fraud

3. Information Sharing
We do not sell, trade, or otherwise transfer your personal information to third parties except:
• With your explicit consent
• To comply with legal obligations
• To protect our rights and safety
• With service providers who assist in our operations

4. Data Security
We implement appropriate security measures to protect your information:
• Encryption of data in transit and at rest
• Regular security audits and updates
• Access controls and authentication
• Secure data centers and infrastructure

5. Your Rights and Choices
You have the right to:
• Access your personal information
• Correct inaccurate data
• Request deletion of your data
• Export your data
• Opt-out of marketing communications
• Withdraw consent for data processing

6. Cookies and Tracking
We use cookies and similar technologies to:
• Maintain your session
• Remember your preferences
• Analyze platform usage
• Improve user experience
• Provide personalized content

7. Data Retention
We retain your data for:
• As long as your account is active
• As required by law
• As necessary to provide our services
• Until you request deletion

8. International Data Transfers
Your data may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place for such transfers in compliance with applicable data protection laws.

9. Children's Privacy
Our services are not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13.

10. Changes to Privacy Policy
We may update this privacy policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "Last Updated" date.

11. Contact Us
If you have any questions about this Privacy Policy, please contact us at:
Email: privacy@example.com
Address: [Your Company Address]
Phone: [Your Company Phone]`,
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
              {content?.title || 'Privacy Policy'}
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
