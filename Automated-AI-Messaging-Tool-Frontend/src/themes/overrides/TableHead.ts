// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - TABLE HEAD ||============================== //

export default function TableHead(theme: Theme) {
  return {
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: '#F9FAFB', // Light gray background
          borderTop: '1px solid #E5E7EB', // Light gray border
          borderBottom: '2px solid #E5E7EB', // Thicker bottom border
          '& .MuiTableCell-head': {
            color: '#111827', // Very dark gray text
            fontWeight: 600, // Medium font weight
            fontSize: '0.875rem',
            textTransform: 'none' // No uppercase transformation
          }
        }
      }
    }
  };
}
