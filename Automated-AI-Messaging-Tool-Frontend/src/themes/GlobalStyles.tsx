'use client';

import { GlobalStyles as MuiGlobalStyles } from '@mui/material';

// ==============================|| THEME - GLOBAL STYLE  ||============================== //

export default function GlobalStyles() {
  return (
    <MuiGlobalStyles
      styles={{
        '@import': [
          'url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap")'
        ],
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
        },
        ul: {
          margin: 0,
          padding: 0
        },
        // Custom utility classes for the new color scheme
        '.bg-light-blue': {
          backgroundColor: '#e6f3ff'
        },
        '.text-primary-color': {
          color: '#0f172a'
        },
        '.text-paragraph-color': {
          color: '#9095a4'
        },
        '.text-icon-color': {
          color: '#71767b'
        },
        '.bg-button-color': {
          backgroundColor: '#6200ff'
        },
        // Force all Material-UI Typography components to use Poppins font
        '[class*="MuiTypography-root"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important'
        },
        '[class*="MuiTypography-h1"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#0f172a !important'
        },
        '[class*="MuiTypography-h2"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#0f172a !important'
        },
        '[class*="MuiTypography-h3"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#0f172a !important'
        },
        '[class*="MuiTypography-h4"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#0f172a !important'
        },
        '[class*="MuiTypography-h5"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#0f172a !important'
        },
        '[class*="MuiTypography-h6"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#0f172a !important'
        },
        '[class*="MuiTypography-body1"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#9095a4 !important'
        },
        '[class*="MuiTypography-body2"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#9095a4 !important'
        },
        '[class*="MuiTypography-subtitle1"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#9095a4 !important'
        },
        '[class*="MuiTypography-subtitle2"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#9095a4 !important'
        },
        '[class*="MuiTypography-caption"]': {
          fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif !important',
          color: '#71767b !important'
        }
      }}
    />
  );
}
