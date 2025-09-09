// material-ui
import { Theme } from '@mui/material/styles';

// project-imports
import getColors from 'utils/getColors';

// types
import { ExtendedStyleProps } from 'types/extended';

function getColorStyle({ color, theme }: ExtendedStyleProps) {
  const colors = getColors(theme, color);
  const { main } = colors;

  return {
    border: `2px solid ${main}`
  };
}

// ==============================|| OVERRIDES - SLIDER ||============================== //

export default function Slider(theme: Theme) {
  return {
    MuiSlider: {
      styleOverrides: {
        track: {
          height: '4px',
          borderRadius: '2px',
          backgroundColor: '#7B3FF2'
        },
        thumb: {
          width: 20,
          height: 20,
          border: '2px solid #7B3FF2',
          backgroundColor: '#FFFFFF',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
          transition: 'all 0.2s ease',
          '&:hover': {
            transform: 'scale(1.1)',
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)'
          },
          '&.MuiSlider-thumbColorPrimary': getColorStyle({ color: 'primary', theme }),
          '&.MuiSlider-thumbColorSecondary': getColorStyle({ color: 'secondary', theme }),
          '&.MuiSlider-thumbColorSuccess': getColorStyle({ color: 'success', theme }),
          '&.MuiSlider-thumbColorWarning': getColorStyle({ color: 'warning', theme }),
          '&.MuiSlider-thumbColorInfo': getColorStyle({ color: 'info', theme }),
          '&.MuiSlider-thumbColorError': getColorStyle({ color: 'error', theme })
        },
        mark: {
          width: 6,
          height: 6,
          borderRadius: '50%',
          border: '1px solid #D1D5DB',
          backgroundColor: '#FFFFFF',
          '&.MuiSlider-markActive': {
            opacity: 1,
            borderColor: '#7B3FF2',
            borderWidth: 2,
            backgroundColor: '#7B3FF2'
          }
        },
        rail: {
          color: '#E5E7EB',
          height: '4px',
          borderRadius: '2px'
        },
        root: {
          '&.Mui-disabled': {
            '.MuiSlider-rail': {
              opacity: 0.25
            },
            '.MuiSlider-track': {
              color: '#D1D5DB'
            },
            '.MuiSlider-thumb': {
              border: '2px solid #D1D5DB'
            }
          }
        },
        valueLabel: {
          backgroundColor: '#7B3FF2',
          color: '#FFFFFF',
          borderRadius: '8px',
          fontSize: '0.875rem',
          fontWeight: 500,
          padding: '4px 8px'
        }
      }
    }
  };
}
