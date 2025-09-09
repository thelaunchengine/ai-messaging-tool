// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - ICON BUTTON ||============================== //

export default function IconButton(theme: Theme) {
  return {
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          transition: 'all 0.2s ease',
          color: '#71767b', // New icon color
          '&:hover': {
            backgroundColor: '#F3F4F6',
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          },
          '&.MuiIconButton-loading': {
            pointerEvents: 'none !important',
            '& svg': {
              width: 'inherit !important',
              height: 'inherit !important'
            }
          }
        },
        sizeLarge: {
          width: theme.spacing(5.5),
          height: theme.spacing(5.5),
          fontSize: '1.25rem',
          borderRadius: '16px',
          '& svg': {
            width: 24,
            height: 24
          }
        },
        sizeMedium: {
          width: theme.spacing(4.5),
          height: theme.spacing(4.5),
          fontSize: '1rem',
          borderRadius: '12px',
          '& svg': {
            width: 20,
            height: 20
          }
        },
        sizeSmall: {
          width: theme.spacing(3.75),
          height: theme.spacing(3.75),
          fontSize: '0.85rem',
          borderRadius: '10px',
          '& svg': {
            width: 16,
            height: 16
          }
        }
      }
    }
  };
}
