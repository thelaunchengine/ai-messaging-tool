'use client';

// project-imports
import { ThemeMode } from '../types/config';

// ==============================|| DEFAULT THEME - TYPOGRAPHY  ||============================== //

export default function Typography(mode: ThemeMode) {
  return {
    fontFamily: 'Poppins, Inter, Roboto, Arial, sans-serif',
    h1: {
      fontWeight: 800,
      fontSize: '2.5rem',
      lineHeight: 1.2
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
      lineHeight: 1.25
    },
    h3: {
      fontWeight: 700,
      fontSize: '1.5rem',
      lineHeight: 1.3
    },
    h4: {
      fontWeight: 700,
      fontSize: '1.25rem',
      lineHeight: 1.35
    },
    h5: {
      fontWeight: 700,
      fontSize: '1.1rem',
      lineHeight: 1.4
    },
    h6: {
      fontWeight: 700,
      fontSize: '1rem',
      lineHeight: 1.5
    },
    subtitle1: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.5
    },
    subtitle2: {
      fontSize: '0.95rem',
      fontWeight: 500,
      lineHeight: 1.6
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.6
    },
    body2: {
      fontSize: '0.95rem',
      fontWeight: 400,
      lineHeight: 1.7
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      fontSize: '1rem',
      letterSpacing: '0.02em'
    },
    caption: {
      fontSize: '0.9rem',
      fontWeight: 400,
      lineHeight: 1.6
    },
    overline: {
      fontSize: '0.85rem',
      fontWeight: 500,
      lineHeight: 1.6
    }
  };
}
