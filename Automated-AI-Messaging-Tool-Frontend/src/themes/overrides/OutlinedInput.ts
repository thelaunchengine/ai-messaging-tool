// material-ui
import { Theme } from '@mui/material/styles';

// project-imports
import getColors from 'utils/getColors';
import getShadow from 'utils/getShadow';

// types
import { ColorProps } from 'types/extended';

interface Props {
  variant: ColorProps;
  theme: Theme;
}

// ==============================|| OVERRIDES - INPUT BORDER & SHADOWS ||============================== //

function getColor({ variant, theme }: Props) {
  const colors = getColors(theme, variant);
  const { light } = colors;

  const shadows = getShadow(theme, `${variant}`);

  return {
    '&:hover .MuiOutlinedInput-notchedOutline': {
      borderColor: '#7B3FF2', // Purple border on hover
      borderWidth: '2px'
    },
    '&.Mui-focused': {
      boxShadow: '0 0 0 3px rgba(123, 63, 242, 0.1)', // Purple focus ring
      '& .MuiOutlinedInput-notchedOutline': {
        border: '2px solid',
        borderColor: '#7B3FF2' // Purple border when focused
      }
    }
  };
}

// ==============================|| OVERRIDES - OUTLINED INPUT ||============================== //

export default function OutlinedInput(theme: Theme) {
  return {
    MuiOutlinedInput: {
      styleOverrides: {
        input: {
          padding: '16px 20px', // Increased padding
          fontSize: '0.875rem', // Consistent font size
          '&::placeholder': {
            color: '#9CA3AF', // Light gray placeholder
            opacity: 1
          }
        },
        notchedOutline: {
          borderColor: '#E5E7EB', // Light gray border
          borderWidth: '1px',
          borderRadius: '12px', // Rounded corners
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)' // Smooth transition
        },
        root: {
          borderRadius: '12px', // Rounded corners
          backgroundColor: '#FFFFFF', // White background
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)', // Smooth transition
          '&:hover': {
            backgroundColor: '#F9FAFB' // Light gray background on hover
          },
          '& svg': {
            color: '#7B3FF2' // Purple icons
          },
          ...getColor({ variant: 'primary', theme }),
          '&.Mui-error': {
            ...getColor({ variant: 'error', theme }),
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: '#EF4444' // Red border for error
            }
          },
          '&.Mui-disabled': {
            backgroundColor: '#F3F4F6', // Light gray background when disabled
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: '#D1D5DB' // Light gray border when disabled
            }
          }
        },
        inputSizeSmall: {
          padding: '12px 16px', // Smaller padding for small size
          fontSize: '0.75rem'
        },
        inputMultiline: {
          padding: '16px 20px', // Consistent padding for multiline
          lineHeight: '1.5'
        },
        colorSecondary: getColor({ variant: 'secondary', theme }),
        colorError: getColor({ variant: 'error', theme }),
        colorWarning: getColor({ variant: 'warning', theme }),
        colorInfo: getColor({ variant: 'info', theme }),
        colorSuccess: getColor({ variant: 'success', theme })
      }
    }
  };
}
