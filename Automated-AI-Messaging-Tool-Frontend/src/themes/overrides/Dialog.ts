// material-ui
import { alpha } from '@mui/material/styles';

// ==============================|| OVERRIDES - DIALOG ||============================== //

export default function Dialog() {
  return {
    MuiDialog: {
      styleOverrides: {
        root: {
          '& .MuiBackdrop-root': {
            backgroundColor: alpha('#000', 0.6)
          }
        },
        paper: {
          backgroundImage: 'none',
          borderRadius: '16px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          border: '1px solid #E5E7EB',
          maxWidth: '90vw',
          maxHeight: '90vh'
        }
      }
    }
  };
}
