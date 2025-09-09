// material-ui
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';

// project-imports
import Avatar from 'components/@extended/Avatar';
import MainCard from 'components/MainCard';

// types
import { SizeProps } from 'types/extended';
import { GenericCardProps } from 'types/root';

interface Props {
  primary: string;
  secondary: string;
  content: string;
  iconPrimary: GenericCardProps['iconPrimary'];
  color: string;
  bgcolor: string;
  avatarSize?: SizeProps;
  circular?: boolean;
}

// ============================|| STATISTICS - ROUND ICON CARD ||============================ //

export default function RoundIconCard({ primary, secondary, content, iconPrimary, color, bgcolor, avatarSize = 'lg', circular }: Props) {
  const IconPrimary = iconPrimary!;
  const primaryIcon = iconPrimary ? <IconPrimary style={{ fontSize: 40 }} /> : null;

  return (
    <MainCard>
      <Grid container sx={{ alignItems: 'center', justifyContent: 'space-between', minHeight: 120 }}>
        <Grid>
          <Stack sx={{ gap: 2 }}>
            <Typography variant="h5" color="inherit">
              {primary}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              {secondary}
            </Typography>
            <Typography variant="subtitle2" color="inherit">
              {content}
            </Typography>
          </Stack>
        </Grid>
        <Grid>
          <Avatar
            variant={circular ? 'circular' : 'rounded'}
            sx={{
              bgcolor: bgcolor || 'primary.main',
              color: color || '#fff',
              width: 56,
              height: 56,
              boxShadow: '0 2px 8px rgba(70,128,255,0.10)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'box-shadow 0.2s',
              '&:hover': {
                boxShadow: '0 4px 16px rgba(70,128,255,0.18)'
              }
            }}
            size={avatarSize}
          >
            {primaryIcon}
          </Avatar>
        </Grid>
      </Grid>
    </MainCard>
  );
}
