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
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import MainCard from '../../../components/MainCard';

interface ContentData {
  title: string;
  content: string;
  lastUpdated?: string;
  status?: string;
}

const defaultFaqs = [
  {
    question: 'How do I get started with AI Messaging Tool?',
    answer:
      'Upload your CSV file with website URLs, configure your AI settings, and start processing. The system will automatically analyze websites and generate personalized messages.'
  },
  {
    question: 'What file formats are supported?',
    answer: 'We support CSV and Excel files (.csv, .xlsx, .xls) containing website URLs and contact form URLs.'
  },
  {
    question: 'How does the AI message generation work?',
    answer:
      'Our AI analyzes the "About Us" content of each website to understand the business context and generates personalized messages that are relevant and engaging.'
  },
  {
    question: 'Can I customize the message templates?',
    answer:
      'Yes, you can create and manage custom message templates in the admin panel. These templates can include variables that get replaced with specific business information.'
  },
  {
    question: 'How do I track the success of my messages?',
    answer:
      'The platform provides comprehensive analytics including delivery status, success rates, and detailed reports that you can download and analyze.'
  },
  {
    question: 'Is my data secure?',
    answer:
      'Yes, we implement enterprise-grade security measures to protect your data. All communications are encrypted and we follow strict data protection protocols.'
  }
];

export default function HelpPage() {
  const [content, setContent] = useState<ContentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchContent = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/content?type=help');

        if (response.ok) {
          const data = await response.json();
          setContent(data.content);
        } else {
          // If no content found, use default content
          setContent({
            title: 'Help & Support',
            content: `Welcome to the AI Messaging Tool Help Center. Here you'll find comprehensive guides, tutorials, and answers to frequently asked questions to help you get the most out of our platform.

Getting Started:
Our platform is designed to be intuitive and easy to use. Follow our step-by-step guides to set up your account, upload your first file, and start generating AI-powered messages.

Key Features:
• Automated website analysis
• AI-powered message generation
• Contact form detection and submission
• Comprehensive analytics and reporting
• Custom message templates
• Multi-format file support

Need More Help?
If you can't find the answer you're looking for, our support team is here to help. Contact us through the support chat or email us directly.`,
            lastUpdated: new Date().toLocaleDateString(),
            status: 'published'
          });
        }
      } catch (err) {
        setError('Failed to load content. Please try again later.');
        // Set default content on error
        setContent({
          title: 'Help & Support',
          content: `Welcome to the AI Messaging Tool Help Center. Here you'll find comprehensive guides, tutorials, and answers to frequently asked questions to help you get the most out of our platform.

Getting Started:
Our platform is designed to be intuitive and easy to use. Follow our step-by-step guides to set up your account, upload your first file, and start generating AI-powered messages.

Key Features:
• Automated website analysis
• AI-powered message generation
• Contact form detection and submission
• Comprehensive analytics and reporting
• Custom message templates
• Multi-format file support

Need More Help?
If you can't find the answer you're looking for, our support team is here to help. Contact us through the support chat or email us directly.`,
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
              Help & Support
            </Typography>
          </Box>
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
              {content?.content || 'Content not available.'}
            </Typography>
          </Paper>
          <Box>
            <Typography variant="h5" fontWeight={700} sx={{ color: '#23272E', mb: 2 }}>
              Frequently Asked Questions
            </Typography>
            <Stack spacing={2}>
              {defaultFaqs.map((faq, index) => (
                <Accordion key={index} variant="outlined">
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">{faq.question}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body1" color="text.secondary">
                      {faq.answer}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Stack>
          </Box>
          <Box sx={{ mt: 4, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Still need help? Contact our support team through the admin panel or email us at support@aimessagingtool.com
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
