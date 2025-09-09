// material-ui
import { Theme } from '@mui/material/styles';

// project-imports
import getColors from 'utils/getColors';

// types
import { ExtendedStyleProps } from 'types/extended';

// ==============================|| BADGE - COLORS ||============================== //

function getColorStyle({ color, theme }: ExtendedStyleProps) {
  const colors = getColors(theme, color);
  const { darker, lighter } = colors;

  return {
    color: darker,
    backgroundColor: lighter
  };
}

// ==============================|| OVERRIDES - BADGE ||============================== //

export default function Badge(theme: Theme) {
  const defaultLightBadge = getColorStyle({ color: 'primary', theme });

  return {
    MuiBadge: {
      styleOverrides: {
        standard: {
          minWidth: theme.spacing(2.5),
          height: theme.spacing(2.5),
          padding: theme.spacing(0.75),
          borderRadius: '12px',
          fontSize: '0.75rem',
          fontWeight: 600,
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        },
        colorSecondary: {
          color: '#7B3FF2',
          backgroundColor: '#F3F4F6'
        },
        light: {
          ...defaultLightBadge,
          borderRadius: '12px',
          fontSize: '0.75rem',
          fontWeight: 600,
          boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
          '&.MuiBadge-colorPrimary': getColorStyle({ color: 'primary', theme }),
          '&.MuiBadge-colorSecondary': getColorStyle({ color: 'secondary', theme }),
          '&.MuiBadge-colorError': getColorStyle({ color: 'error', theme }),
          '&.MuiBadge-colorInfo': getColorStyle({ color: 'info', theme }),
          '&.MuiBadge-colorSuccess': getColorStyle({ color: 'success', theme }),
          '&.MuiBadge-colorWarning': getColorStyle({ color: 'warning', theme })
        }
      }
    }
  };
}
