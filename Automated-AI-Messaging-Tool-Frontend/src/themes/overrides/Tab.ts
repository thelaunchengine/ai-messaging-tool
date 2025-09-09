// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - TAB ||============================== //

export default function Tab(theme: Theme) {
  return {
    MuiTab: {
      styleOverrides: {
        root: {
          minHeight: 48,
          color: '#374151',
          borderRadius: '8px',
          fontSize: '0.875rem',
          fontWeight: 500,
          textTransform: 'none',
          transition: 'all 0.2s ease',
          '&:hover': {
            color: '#7B3FF2',
            backgroundColor: '#F3F4F6'
          },
          '&.Mui-selected': {
            color: '#7B3FF2',
            fontWeight: 600
          },
          '&:focus-visible': {
            borderRadius: '8px',
            outline: `2px solid #7B3FF2`,
            outlineOffset: -3
          },
          '& svg.MuiTab-iconWrapper': {
            width: 20,
            height: 20,
            marginBottom: '4px'
          }
        }
      }
    }
  };
}
