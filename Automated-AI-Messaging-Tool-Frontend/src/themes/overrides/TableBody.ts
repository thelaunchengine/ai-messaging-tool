// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - TABLE BODY ||============================== //

export default function TableBody(theme: Theme) {
  const hoverStyle = {
    '&:hover': {
      backgroundColor: '#F3F4F6', // Light gray hover effect
      transition: 'background-color 0.2s ease'
    }
  };

  return {
    MuiTableBody: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF', // White background
          '&.striped .MuiTableRow-root': {
            '&:nth-of-type(even)': {
              backgroundColor: '#F9FAFB' // Very light gray for striped rows
            },
            ...hoverStyle
          },
          '& .MuiTableRow-root': {
            borderBottom: '1px solid #E5E7EB', // Light border between rows
            ...hoverStyle
          }
        }
      }
    }
  };
}
