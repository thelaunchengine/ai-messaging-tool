// material-ui
import { alpha, Theme } from '@mui/material/styles';

// project-imports
import getColors from 'utils/getColors';

// types
import { ExtendedStyleProps } from 'types/extended';

// ==============================|| ALERT - COLORS ||============================== //

function getColorStyle({ color, theme }: ExtendedStyleProps) {
  const colors = getColors(theme, color);
  const { lighter, light, main, darker } = colors;

  return {
    borderColor: alpha(light, 0.5),
    backgroundColor: lighter,
    '& .MuiAlert-icon': {
      color: main,
      ...theme.applyStyles('dark', { color: darker })
    }
  };
}

// ==============================|| OVERRIDES - ALERT ||============================== //

export default function Alert(theme: Theme) {
  const primaryDashed = getColorStyle({ color: 'primary', theme });

  return {
    MuiAlert: {
      styleOverrides: {
        root: {
          color: theme.palette.text.primary,
          fontSize: '0.875rem',
          borderRadius: '12px',
          padding: '12px 16px',
          border: '1px solid transparent',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        },
        icon: {
          '& svg': {
            width: 20,
            height: 20
          }
        },
        message: {
          padding: 0,
          marginTop: 3,
          fontWeight: 500
        },
        filled: {
          color: theme.palette.background.default,
          border: 'none'
        },
        border: {
          padding: '12px 16px',
          border: '1px solid',
          borderRadius: '12px',
          ...primaryDashed,
          '&.MuiAlert-borderPrimary': getColorStyle({ color: 'primary', theme }),
          '&.MuiAlert-borderSecondary': getColorStyle({ color: 'secondary', theme }),
          '&.MuiAlert-borderError': getColorStyle({ color: 'error', theme }),
          '&.MuiAlert-borderSuccess': getColorStyle({ color: 'success', theme }),
          '&.MuiAlert-borderInfo': getColorStyle({ color: 'info', theme }),
          '&.MuiAlert-borderWarning': getColorStyle({ color: 'warning', theme })
        },
        action: {
          '& .MuiButton-root': {
            padding: 2,
            height: 'auto',
            fontSize: '0.85rem',
            marginTop: -2,
            borderRadius: '8px'
          },
          '& .MuiIconButton-root': {
            width: 'auto',
            height: 'auto',
            padding: 2,
            marginRight: 6,
            borderRadius: '8px',
            '& .MuiSvgIcon-root': {
              fontSize: '1rem'
            }
          }
        }
      }
    }
  };
}
