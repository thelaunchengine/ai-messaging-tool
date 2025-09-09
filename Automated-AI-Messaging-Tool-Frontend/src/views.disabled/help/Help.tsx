'use client';

import { useState } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';

// project-imports
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

// assets
import { Search, Document, MessageQuestion, Setting2, Chart2 } from '@wandersonalwes/iconsax-react';

// ==============================|| HELP ||============================== //

export default function Help() {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState('');

  const faqs = [
    {
      question: 'How do I get started with the AI Messaging Tool?',
      answer:
        'To get started, first upload your list of websites in CSV or Excel format. Then, configure your AI model settings and message templates. Finally, start the automation process and monitor the results in real-time.'
    },
    {
      question: 'What file formats are supported for website lists?',
      answer:
        'The tool supports CSV and Excel files (.csv, .xlsx). Your file should contain columns for website URLs and optional contact form URLs.'
    },
    {
      question: 'How do I customize message templates?',
      answer:
        'You can customize message templates in the Settings page. Use variables like {website}, {business_type}, {company_name}, and {industry} to create dynamic messages.'
    },
    {
      question: 'What AI models are supported?',
      answer: 'Currently, we support GPT-4, GPT-3.5, and Gemini. You can select your preferred model in the Settings page.'
    },
    {
      question: 'How do I handle failed messages?',
      answer:
        'Failed messages are automatically logged in the Processing Status page. You can retry failed messages individually or in bulk. The system will also provide reasons for failures.'
    }
  ];

  const guides = [
    {
      title: 'Getting Started Guide',
      icon: <Document />,
      description: 'Learn the basics of setting up and using the AI Messaging Tool'
    },
    {
      title: 'Message Templates',
      icon: <MessageQuestion />,
      description: 'How to create and customize effective message templates'
    },
    {
      title: 'Configuration Guide',
      icon: <Setting2 />,
      description: 'Detailed guide on configuring AI models and automation settings'
    },
    {
      title: 'Analytics & Reporting',
      icon: <Chart2 />,
      description: 'Understanding your automation results and performance metrics'
    }
  ];

  return (
    <Grid container spacing={GRID_COMMON_SPACING}>
      <Grid size={12}>
        <Stack spacing={3}>
          <Typography variant="h3">Help & Documentation</Typography>

          <TextField
            fullWidth
            placeholder="Search help articles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              )
            }}
          />
        </Stack>
      </Grid>

      <Grid size={12} md={8}>
        <MainCard title="Frequently Asked Questions">
          <Stack spacing={2}>
            {faqs.map((faq, index) => (
              <Accordion key={index}>
                <AccordionSummary>
                  <Typography variant="subtitle1">{faq.question}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography>{faq.answer}</Typography>
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        </MainCard>
      </Grid>

      <Grid size={12} md={4}>
        <MainCard title="Quick Guides">
          <List>
            {guides.map((guide, index) => (
              <div key={index}>
                <ListItem button>
                  <ListItemIcon>{guide.icon}</ListItemIcon>
                  <ListItemText primary={guide.title} secondary={guide.description} />
                </ListItem>
                {index < guides.length - 1 && <Divider />}
              </div>
            ))}
          </List>
        </MainCard>

        <MainCard title="Need More Help?" sx={{ mt: 2 }}>
          <Stack spacing={2}>
            <Typography>Can't find what you're looking for? Our support team is here to help.</Typography>
            <Button variant="contained" color="primary" fullWidth>
              Contact Support
            </Button>
          </Stack>
        </MainCard>
      </Grid>
    </Grid>
  );
}
