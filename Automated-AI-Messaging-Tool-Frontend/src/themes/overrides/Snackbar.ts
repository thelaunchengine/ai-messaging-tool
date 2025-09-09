// material-ui
import { alpha, Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - SNACKBAR ||============================== //

export default function Snackbar(theme: Theme) {
  return {
    MuiSnackbar: {
      styleOverrides: {
        root: {
          '& .MuiAlert-root': {
            borderRadius: '12px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
            border: '1px solid #E5E7EB',
            '& .MuiAlert-message': {
              marginTop: 4,
              fontSize: '0.875rem',
              fontWeight: 500,
              '& .MuiButton-root': {
                marginTop: 2,
                borderRadius: '8px',
                fontSize: '0.75rem'
              }
            },
            '& .MuiAlert-action': {
              '& .MuiButton-root': {
                marginRight: 4,
                marginTop: 0,
                borderRadius: '8px',
                fontSize: '0.75rem'
              },
              '& .MuiIconButton-root': {
                color: '#374151',
                borderRadius: '8px',
                transition: 'all 0.2s ease',
                '&.MuiIconButton-colorSecondary': {
                  backgroundColor: '#7B3FF2',
                  color: '#FFFFFF',
                  '&:hover': {
                    backgroundColor: '#6B21A8'
                  }
                },
                '&:hover': {
                  backgroundColor: '#F3F4F6'
                }
              }
            },
            '&:not(.MuiAlert-outlined)': {
              '& .MuiAlert-action': {
                '& .MuiIconButton-root': {
                  '&:hover': {
                    backgroundColor: alpha('#374151', 0.1)
                  }
                }
              }
            }
          }
        }
      }
    }
  };
}
