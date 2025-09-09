// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - LIST ITEM BUTTON ||============================== //

export default function ListItemButton(theme: Theme) {
  return {
    MuiListItemButton: {
      styleOverrides: {
        root: {
          color: theme.palette.secondary.main,
          borderRadius: 8,
          marginTop: 0,
          marginBottom: 0,
          '&.Mui-selected': {
            backgroundColor: '#6100FF !important',
            color: '#FFFFFF !important',
            fontWeight: 700,
            '& .MuiListItemIcon-root': {
              color: '#FFFFFF !important',
            },
            '& .MuiTypography-root': {
              color: '#FFFFFF !important',
            }
          },
          '&.Mui-selected:hover': {
            backgroundColor: '#6100FF !important',
            color: '#FFFFFF !important',
            '& .MuiListItemIcon-root': {
              color: '#FFFFFF !important',
            },
            '& .MuiTypography-root': {
              color: '#FFFFFF !important',
            }
          },
          '&:hover': {
            backgroundColor: '#E8EFFF !important',
          },
        }
      }
    }
  };
}
