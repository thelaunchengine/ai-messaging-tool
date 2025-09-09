// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - TOOLTIP ||============================== //

export default function Tooltip(theme: Theme) {
  return {
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: '#374151', // Dark gray background
          color: '#FFFFFF', // White text
          fontSize: '0.75rem', // Consistent font size
          fontWeight: 500, // Medium font weight
          borderRadius: '8px', // Rounded corners
          padding: '8px 12px', // Better padding
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)', // Enhanced shadow
          border: '1px solid #E5E7EB', // Light border
          maxWidth: '300px', // Maximum width
          lineHeight: 1.4 // Better line height
        },
        arrow: {
          color: '#374151' // Dark gray arrow
        }
      }
    }
  };
}
