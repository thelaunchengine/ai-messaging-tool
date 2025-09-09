// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - ACCORDION ||============================== //

export default function Accordion(theme: Theme) {
  return {
    MuiAccordion: {
      defaultProps: {
        disableGutters: true,
        square: false,
        elevation: 0
      },
      styleOverrides: {
        root: {
          border: '1px solid #E5E7EB',
          borderRadius: '12px',
          marginBottom: '8px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          transition: 'all 0.2s ease',
          '&:not(:last-child)': {
            borderBottom: '1px solid #E5E7EB'
          },
          '&:before': {
            display: 'none'
          },
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          },
          '&.Mui-disabled': {
            backgroundColor: '#F9FAFB'
          },
          '&.Mui-expanded': {
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
          }
        }
      }
    }
  };
}
