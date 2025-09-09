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
          height: '100%'
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
          borderRadius: '8px'
        },
        contained: {
          backgroundColor: '#3F3F3F !important',
          color: '#FEFEFE !important',
          '&:hover': {
            backgroundColor: '#2A2A2A !important'
          },
          '&:disabled': {
            backgroundColor: '#CCCCCC !important',
            color: '#666666 !important'
          }
        },
        outlined: {
          color: '#3F3F3F !important',
          borderColor: '#3F3F3F !important',
          backgroundColor: '#FEFEFE !important',
          '&:hover': {
            backgroundColor: '#F5F5F5 !important',
            borderColor: '#2A2A2A !important'
          },
          '&:disabled': {
            color: '#CCCCCC !important',
            borderColor: '#CCCCCC !important',
            backgroundColor: '#FEFEFE !important'
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
          color: '#3F3F3F !important',
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
          color: '#3F3F3F !important',
          '&:hover': {
            backgroundColor: '#F5F5F5 !important'
          }
        }
      }
    },

  };
}
