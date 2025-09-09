'use client';

import { createTheme } from '@mui/material/styles';

const theme = () => {
  return createTheme({
    palette: {
      mode: 'light',
      primary: {
        main: '#6200ff',
        contrastText: '#fff'
      },
      secondary: {
        main: '#71767b',
        contrastText: '#fff'
      },
      error: {
        main: '#dc2626'
      },
      warning: {
        main: '#e58a00'
      },
      info: {
        main: '#71767b'
      },
      success: {
        main: '#2ca87f'
      },
      grey: {
        50: '#fafafa',
        100: '#f5f5f5',
        200: '#eeeeee',
        300: '#e0e0e0',
        400: '#bdbdbd',
        500: '#9e9e9e',
        600: '#757575',
        700: '#616161',
        800: '#424242',
        900: '#212121'
      }
    },
    components: {
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            height: 6,
            borderRadius: 100,
            backgroundColor: '#f5f5f5'
          },
          bar: {
            borderRadius: 100,
            backgroundColor: '#6200ff'
          }
        }
      }
    }
  });
};

export default theme;
