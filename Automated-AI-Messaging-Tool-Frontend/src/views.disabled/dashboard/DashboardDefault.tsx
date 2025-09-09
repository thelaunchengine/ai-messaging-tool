'use client';

// material-ui
import { useTheme } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

// project-imports
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

// assets
import { DocumentUpload, Globe, MessageQuestion, User } from '@wandersonalwes/iconsax-react';

// ==============================|| DASHBOARD - DEFAULT ||============================== //

export default function DashboardDefault() {
  const theme = useTheme();

  return (
    <Grid container spacing={GRID_COMMON_SPACING}>
      {/* Statistics Cards */}
      <Grid size={{ xs: 12, md: 6, lg: 3 }}>
        <MainCard>
          <Stack direction="row" spacing={2} alignItems="center">
            <Stack spacing={0.5}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Total Files
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                150
              </Typography>
            </Stack>
            <DocumentUpload style={{ fontSize: '2rem', color: theme.palette.primary.main }} />
          </Stack>
        </MainCard>
      </Grid>
      <Grid size={{ xs: 12, md: 6, lg: 3 }}>
        <MainCard>
          <Stack direction="row" spacing={2} alignItems="center">
            <Stack spacing={0.5}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Total Websites
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                1,250
              </Typography>
            </Stack>
            <Globe style={{ fontSize: '2rem', color: theme.palette.success.main }} />
          </Stack>
        </MainCard>
      </Grid>
      <Grid size={{ xs: 12, md: 6, lg: 3 }}>
        <MainCard>
          <Stack direction="row" spacing={2} alignItems="center">
            <Stack spacing={0.5}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Messages Sent
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                850
              </Typography>
            </Stack>
            <MessageQuestion style={{ fontSize: '2rem', color: theme.palette.warning.main }} />
          </Stack>
        </MainCard>
      </Grid>
      <Grid size={{ xs: 12, md: 6, lg: 3 }}>
        <MainCard>
          <Stack direction="row" spacing={2} alignItems="center">
            <Stack spacing={0.5}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Active Users
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                25
              </Typography>
            </Stack>
            <User style={{ fontSize: '2rem', color: theme.palette.error.main }} />
          </Stack>
        </MainCard>
      </Grid>

      {/* File Upload Section */}
      <Grid size={12}>
        <MainCard title="Upload Website List">
          <Stack spacing={3}>
            <Typography variant="body2" color="textSecondary">
              Upload a CSV or Excel file containing website URLs and their corresponding Contact Form URLs.
            </Typography>
            <Stack
              sx={{
                border: '1px dashed',
                borderColor: 'divider',
                borderRadius: 1,
                p: 3,
                textAlign: 'center'
              }}
            >
              <DocumentUpload style={{ fontSize: '3rem', color: theme.palette.primary.main, margin: '0 auto' }} />
              <Typography variant="h6" sx={{ mt: 2 }}>
                Drag & Drop or Click to Upload
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Supported formats: .csv, .xlsx
              </Typography>
            </Stack>
          </Stack>
        </MainCard>
      </Grid>

      {/* Recent Activity */}
      <Grid size={12}>
        <MainCard title="Recent Activity">
          <Stack spacing={2}>
            {[1, 2, 3].map((item) => (
              <Stack
                key={item}
                direction="row"
                spacing={2}
                sx={{
                  p: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1
                }}
              >
                <DocumentUpload style={{ fontSize: '1.5rem', color: theme.palette.primary.main }} />
                <Stack spacing={0.5}>
                  <Typography variant="subtitle1">File Uploaded</Typography>
                  <Typography variant="body2" color="textSecondary">
                    example{item}.csv - 100 websites processed
                  </Typography>
                </Stack>
                <Typography variant="caption" color="textSecondary" sx={{ ml: 'auto' }}>
                  2 hours ago
                </Typography>
              </Stack>
            ))}
          </Stack>
        </MainCard>
      </Grid>
    </Grid>
  );
}
