'use client';

import { ThemeMode } from '../types/config';

const palette = (mode: ThemeMode) => ({
  mode,
  primary: {
    main: '#3F3F3F', // Dark gray for icons
    light: '#5A5A5A', // Lighter gray
    dark: '#2A2A2A', // Darker gray
    contrastText: '#FEFEFE'
  },
  secondary: {
    main: '#3F3F3F', // Dark gray for secondary icons
    light: '#5A5A5A', // Lighter gray
    dark: '#2A2A2A', // Darker gray
    contrastText: '#FEFEFE'
  },
  background: {
    default: '#FAFAFA', // Main background
    paper: '#fff',
    sidebar: '#7B3FF2', // Sidebar background
    notification: '#7B3FF2' // Notification badge background
  },
  text: {
    primary: '#23272E', // Main content text
    secondary: '#6B7280', // Labels, secondary text
    disabled: '#B0B7C3',
    sidebar: '#fff' // Sidebar text
  },
  divider: '#E5EAF2',
  success: {
    main: '#3F3F3F',
    contrastText: '#FEFEFE'
  },
  error: {
    main: '#3F3F3F',
    contrastText: '#FEFEFE'
  },
  warning: {
    main: '#3F3F3F',
    contrastText: '#FEFEFE'
  },
  info: {
    main: '#3F3F3F', // Dark gray for info icons
    contrastText: '#FEFEFE'
  },
  grey: {
    100: '#F6F8FB',
    200: '#E5EAF2',
    300: '#D1D9E6',
    400: '#B0B7C3',
    500: '#6B7280',
    600: '#23272E'
  }
});

export default palette;
