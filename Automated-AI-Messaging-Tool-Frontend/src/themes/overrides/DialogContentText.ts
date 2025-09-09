// material-ui
import { Theme } from '@mui/material/styles';

// ==============================|| OVERRIDES - DIALOG CONTENT TEXT ||============================== //

export default function DialogContentText(theme: Theme) {
  return {
    MuiDialogContentText: {
      styleOverrides: {
        root: {
          fontSize: '1.05rem',
          color: theme.palette.text.primary
        }
      }
    }
  };
}
