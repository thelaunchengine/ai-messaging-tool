// material-ui
import { Theme } from '@mui/material/styles';

// assets
import { ArrowRight2 } from '@wandersonalwes/iconsax-react';

// ==============================|| OVERRIDES - ACCORDION SUMMARY ||============================== //

export default function AccordionSummary(theme: Theme) {
  const { palette, spacing } = theme;

  return {
    MuiAccordionSummary: {
      defaultProps: {
        expandIcon: <ArrowRight2 size={16} />
      },
      styleOverrides: {
        root: {
          backgroundColor: '#F9FAFB',
          flexDirection: 'row-reverse',
          minHeight: 56,
          borderRadius: '12px 12px 0 0',
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: '#F3F4F6'
          },
          '&.Mui-expanded': {
            backgroundColor: '#F3F4F6'
          }
        },
        expandIconWrapper: {
          color: '#7B3FF2',
          transition: 'transform 0.2s ease',
          '&.Mui-expanded': {
            transform: 'rotate(90deg)'
          }
        },
        content: {
          marginTop: spacing(1.5),
          marginBottom: spacing(1.5),
          marginLeft: spacing(1.5),
          '& .MuiTypography-root': {
            fontSize: '0.875rem',
            fontWeight: 600,
            color: '#111827'
          }
        }
      }
    }
  };
}
