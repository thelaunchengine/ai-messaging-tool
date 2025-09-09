'use client';

import { Theme, Components } from '@mui/material/styles';

export default function componentsOverride(theme: Theme): Components {
  return {
    MuiCssBaseline: {
      styleOverrides: {
        '*': {
          margin: 0,
          padding: 0,
          boxSizing: 'border-box'
        },
        html: {
          width: '100%',
          height: '100%',
          WebkitOverflowScrolling: 'touch'
        },
        body: {
          width: '100%',
          height: '100%',
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif'
        },
        '#root': {
          width: '100%',
          height: '100%'
        },
        input: {
          '&[type=number]': {
            MozAppearance: 'textfield',
            '&::-webkit-outer-spin-button': {
              margin: 0,
              WebkitAppearance: 'none'
            },
            '&::-webkit-inner-spin-button': {
              margin: 0,
              WebkitAppearance: 'none'
            }
          }
        },
        img: {
          display: 'block',
          maxWidth: '100%'
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif'
        },
        contained: {
          backgroundColor: '#6200ff !important', // New button color
          color: '#ffffff !important',
          '&:hover': {
            backgroundColor: '#4a00cc !important' // New hover color
          },
          '&:disabled': {
            backgroundColor: '#CCCCCC !important',
            color: '#666666 !important'
          }
        },
        outlined: {
          color: '#6200ff !important', // New button color
          borderColor: '#6200ff !important', // New border color
          backgroundColor: '#ffffff !important',
          '&:hover': {
            backgroundColor: 'rgba(98, 0, 255, 0.05) !important', // Light purple background
            borderColor: '#4a00cc !important' // Darker border on hover
          },
          '&:disabled': {
            color: '#CCCCCC !important',
            borderColor: '#CCCCCC !important',
            backgroundColor: '#ffffff !important'
          }
        }
      }
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          '& .MuiTouchRipple-root': {
            color: 'rgba(98, 0, 255, 0.3)' // Updated to new color
          }
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          boxShadow: theme.customShadows?.z1
        }
      }
    },
    MuiCardHeader: {
      styleOverrides: {
        root: {
          padding: '16px'
        }
      }
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: '16px'
        }
      }
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '8px'
          }
        }
      }
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: '8px'
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: '8px'
        }
      }
    },
    MuiSvgIcon: {
      styleOverrides: {
        root: {
          color: '#71767b !important', // Updated to new icon color
          // Exclude sidebar icons from this override
          '.MuiDrawer-root &': {
            color: 'inherit !important'
          },
          // Exclude button icons from this override
          '.MuiButton-root &': {
            color: 'inherit !important'
          }
        }
      }
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          color: '#71767b !important', // Updated to new icon color
          '&:hover': {
            backgroundColor: '#F5F5F5 !important'
          }
        }
      }
    },
    MuiTypography: {
      styleOverrides: {
        root: {
          fontSize: '16px', // Base font size
          fontFamily: '"Poppins", "Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
          color: '#0f172a' // Main text color
        },
        h1: {
          fontSize: '2.5rem',
          fontWeight: 700,
          lineHeight: 1.2,
          color: '#0f172a' // Main text color
        },
        h2: {
          fontSize: '2rem',
          fontWeight: 700,
          lineHeight: 1.3,
          color: '#0f172a' // Main text color
        },
        h3: {
          fontSize: '1.75rem',
          fontWeight: 600,
          lineHeight: 1.3,
          color: '#0f172a' // Main text color
        },
        h4: {
          fontSize: '1.5rem',
          fontWeight: 600,
          lineHeight: 1.4,
          color: '#0f172a' // Main text color
        },
        h5: {
          fontSize: '1.25rem',
          fontWeight: 600,
          lineHeight: 1.4,
          color: '#0f172a' // Main text color
        },
        h6: {
          fontSize: '1.125rem',
          fontWeight: 600,
          lineHeight: 1.4,
          color: '#0f172a' // Main text color
        },
        subtitle1: {
          fontSize: '1rem',
          fontWeight: 500,
          lineHeight: 1.5,
          color: '#9095a4' // Paragraph color
        },
        subtitle2: {
          fontSize: '0.875rem',
          fontWeight: 500,
          lineHeight: 1.5,
          color: '#9095a4' // Paragraph color
        },
        body1: {
          fontSize: '1rem',
          fontWeight: 400,
          lineHeight: 1.6,
          color: '#9095a4' // Paragraph color
        },
        body2: {
          fontSize: '0.875rem',
          fontWeight: 400,
          lineHeight: 1.6,
          color: '#9095a4' // Paragraph color
        },
        caption: {
          fontSize: '0.75rem',
          fontWeight: 400,
          lineHeight: 1.5,
          color: '#71767b' // Icons color
        },
        gutterBottom: {
          marginBottom: 16
        }
      }
    }
  };
}
