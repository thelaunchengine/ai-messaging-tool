// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - PAPER ||============================== //

export default function Paper(theme: Theme) {
  return {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF', // White background
          borderRadius: '12px', // Rounded corners
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)', // Subtle shadow
          border: '1px solid #E5E7EB', // Light border
          '&.MuiPaper-elevation1': {
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
          },
          '&.MuiPaper-elevation2': {
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          },
          '&.MuiPaper-elevation3': {
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
          },
          '&.MuiPaper-elevation4': {
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
          }
        },
        outlined: {
          border: '1px solid #E5E7EB', // Light border
          boxShadow: 'none'
        }
      }
    }
  };
} 