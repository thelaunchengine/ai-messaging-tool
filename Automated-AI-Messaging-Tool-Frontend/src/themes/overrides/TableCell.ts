// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - TABLE CELL ||============================== //

export default function TableCell(theme: Theme) {
  const commonCell = {
    '&:not(:last-of-type)': {
      position: 'relative',
      '&:after': {
        position: 'absolute',
        content: '""',
        backgroundColor: '#E5E7EB', // Light gray border
        width: 1,
        height: 'calc(100% - 30px)',
        right: 0,
        top: 16
      }
    }
  };

  return {
    MuiTableCell: {
      styleOverrides: {
        root: {
          fontSize: '0.875rem',
          padding: '16px 12px', // Increased vertical padding
          borderColor: '#E5E7EB', // Light gray border
          color: '#374151', // Dark gray text
          fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
          '&.cell-right': {
            justifyContent: 'flex-end',
            textAlign: 'right',
            '& > *': {
              justifyContent: 'flex-end',
              margin: '0 0 0 auto'
            },
            '& .MuiOutlinedInput-input': {
              textAlign: 'right'
            }
          },
          '&.cell-center': {
            justifyContent: 'center',
            textAlign: 'center',
            '& > *': {
              justifyContent: 'center',
              margin: '0 auto'
            }
          }
        },
        sizeSmall: {
          padding: '12px 8px' // Increased vertical padding for small cells
        },
        head: {
          fontSize: '0.875rem',
          fontWeight: 600, // Medium font weight
          textTransform: 'none', // No uppercase transformation
          color: '#111827', // Very dark gray for headers
          backgroundColor: '#F9FAFB', // Light gray background for headers
          borderBottom: '2px solid #E5E7EB', // Thicker border for headers
          ...commonCell
        },
        footer: {
          fontSize: '0.875rem',
          textTransform: 'none', // No uppercase transformation
          color: '#374151',
          backgroundColor: '#F9FAFB', // Light gray background for footers
          ...commonCell
        }
      }
    }
  };
}
