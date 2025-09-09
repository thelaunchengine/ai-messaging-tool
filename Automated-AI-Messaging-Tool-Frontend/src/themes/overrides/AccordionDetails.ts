// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - ACCORDION DETAILS ||============================== //

export default function AccordionDetails(theme: Theme) {
  return {
    MuiAccordionDetails: {
      styleOverrides: {
        root: {
          padding: theme.spacing(2.5),
          borderTop: '1px solid #E5E7EB',
          backgroundColor: '#FFFFFF',
          borderRadius: '0 0 12px 12px',
          '& .MuiTypography-root': {
            fontSize: '0.875rem',
            color: '#374151',
            lineHeight: 1.6
          }
        }
      }
    }
  };
}
