// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - INPUT LABEL ||============================== //

export default function InputLabel(theme: Theme) {
  return {
    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: '#374151', // Dark gray color
          fontSize: '0.875rem', // Consistent font size
          fontWeight: 500, // Medium font weight
          '&.Mui-focused': {
            color: '#7B3FF2' // Purple color when focused
          }
        },
        outlined: {
          lineHeight: '1.2em',
          '&.MuiInputLabel-sizeSmall': {
            lineHeight: '1.2em',
            fontSize: '0.75rem'
          },
          '&.MuiInputLabel-shrink': {
            background: '#FFFFFF', // White background
            padding: '0 8px',
            marginLeft: -6,
            lineHeight: '1.4375em',
            color: '#7B3FF2', // Purple color when shrunk
            fontWeight: 600 // Bold when shrunk
          }
        }
      }
    }
  };
}
