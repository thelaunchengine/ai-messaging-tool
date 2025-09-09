// material-ui
import { Theme } from '@mui/material/styles';
import { CheckboxProps } from '@mui/material/Checkbox';

// project-imports
import getColors from 'utils/getColors';

// assets
import { Stop, TickSquare, MinusSquare } from '@wandersonalwes/iconsax-react';

// types
import { ExtendedStyleProps } from 'types/extended';

// ==============================|| RADIO - COLORS ||============================== //

function getColorStyle({ color, theme }: ExtendedStyleProps) {
  const colors = getColors(theme, color);
  const { lighter, main, dark } = colors;

  return {
    '&:hover': {
      backgroundColor: color === 'secondary' ? lighter : lighter + 50,
      ...theme.applyStyles('dark', { backgroundColor: color === 'secondary' ? lighter + 50 : lighter + 20 }),
      '& .icon': { borderColor: main }
    },
    '&.Mui-focusVisible': {
      outline: `2px solid ${dark}`,
      outlineOffset: -4
    }
  };
}

// ==============================|| CHECKBOX - SIZE STYLE ||============================== //

interface CheckboxSizeProps {
  size: number;
}

function getSizeStyle(size?: CheckboxProps['size']): CheckboxSizeProps {
  switch (size) {
    case 'small':
      return { size: 20 };
    case 'large':
      return { size: 28 };
    case 'medium':
    default:
      return { size: 24 };
  }
}

// ==============================|| CHECKBOX - STYLE ||============================== //

function checkboxStyle(size?: CheckboxProps['size']) {
  const sizes: CheckboxSizeProps = getSizeStyle(size);

  return {
    '& svg': {
      width: sizes.size,
      height: sizes.size
    }
  };
}

// ==============================|| OVERRIDES - CHECKBOX ||============================== //

export default function Checkbox(theme: Theme) {
  const { palette } = theme;

  return {
    MuiCheckbox: {
      defaultProps: {
        className: 'size-medium',
        icon: <Stop />,
        checkedIcon: <TickSquare variant="Bold" />,
        indeterminateIcon: <MinusSquare variant="Bold" />
      },
      styleOverrides: {
        root: {
          borderRadius: '6px', // Rounded corners
          color: '#7B3FF2', // Purple color for unchecked state
          transition: 'all 0.2s ease', // Smooth transitions
          '&:hover': {
            backgroundColor: '#F3F4F6', // Light gray hover effect
            transform: 'scale(1.05)' // Slight scale effect
          },
          '&.Mui-checked': {
            color: '#7B3FF2' // Purple color for checked state
          },
          '&.size-small': {
            ...checkboxStyle('small')
          },
          '&.size-medium': {
            ...checkboxStyle('medium')
          },
          '&.size-large': {
            ...checkboxStyle('large')
          }
        },
        colorPrimary: getColorStyle({ color: 'primary', theme }),
        colorSecondary: getColorStyle({ color: 'secondary', theme }),
        colorSuccess: getColorStyle({ color: 'success', theme }),
        colorWarning: getColorStyle({ color: 'warning', theme }),
        colorInfo: getColorStyle({ color: 'info', theme }),
        colorError: getColorStyle({ color: 'error', theme })
      }
    }
  };
}
