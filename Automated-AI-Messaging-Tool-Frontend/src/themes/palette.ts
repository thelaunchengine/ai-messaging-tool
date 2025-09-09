'use client';
console.log("🚨��🚨 THEME ALERT: Theme changes are being applied! 🚨🚨🚨");
console.log("This is a simple test message to verify console is working");

import { ThemeMode } from '../types/config';

const palette = (mode: ThemeMode) => ({
  mode,
  // Complete primary color palette
  primary: {
    50: '#f3e8ff',
    100: '#C8D9FF',
    200: '#A3C0FF',
    300: '#8e7cc3',
    400: '#7a1aff',
    500: '#6b21a8',
    600: '#7c3aed',
    700: '#4a00cc',
    800: '#5b21b6',
    900: '#2a0066',
    A100: '#f3e8ff',
    A200: '#C8D9FF',
    A400: '#7a1aff',
    A700: '#4a00cc',
    light: '#7a1aff',
    main: '#6200ff',
    dark: '#4a00cc',
    lighter: '#E9F0FF',
    darker: '#3a0099',
    contrastText: '#ffffff'
  },
  // Complete secondary color palette
  secondary: {
    50: '#f8fafc',
    100: '#F8F9FA',
    200: '#F3F5F7',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
    A100: '#f8fafc',
    A200: '#F8F9FA',
    A400: '#94a3b8',
    A700: '#334155',
    light: '#cbd5e1',
    main: '#64748b',
    dark: '#334155',
    lighter: '#F8F9FA',
    darker: '#0f172a',
    contrastText: '#ffffff'
  },
  // Complete success color palette
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
    A100: '#f0fdf4',
    A200: '#dcfce7',
    A400: '#4ade80',
    A700: '#15803d',
    light: '#86efac',
    main: '#22c55e',
    dark: '#15803d',
    lighter: '#c0e5d9',
    darker: '#107d4f',
    contrastText: '#ffffff'
  },
  // Complete error color palette
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
    A100: '#fef2f2',
    A200: '#fee2e2',
    A400: '#f87171',
    A700: '#b91c1c',
    light: '#fca5a5',
    main: '#dc2626',
    dark: '#b91c1c',
    lighter: '#f5bebe',
    darker: '#c50d0d',
    contrastText: '#ffffff'
  },
  // Complete warning color palette
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
    A100: '#fffbeb',
    A200: '#fef3c7',
    A400: '#fbbf24',
    A700: '#b45309',
    light: '#fcd34d',
    main: '#f59e0b',
    dark: '#b45309',
    lighter: '#f7dcb3',
    darker: '#d35a00',
    contrastText: '#000000'
  },
  // Complete info color palette
  info: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
    A100: '#eff6ff',
    A200: '#dbeafe',
    A400: '#60a5fa',
    A700: '#1d4ed8',
    light: '#93c5fd',
    main: '#3b82f6',
    dark: '#1d4ed8',
    lighter: '#c5eff3',
    darker: '#4a5f54',
    contrastText: '#ffffff'
  },
  // Complete grey color palette
  grey: {
    50: '#fafafa',
    100: '#F6F8FB',
    200: '#E5EAF2',
    300: '#D1D9E6',
    400: '#B0B7C3',
    500: '#9095a4',
    600: '#0f172a',
    700: '#616161',
    800: '#424242',
    900: '#212121',
    A100: '#d5d5d5',
    A200: '#aaaaaa',
    A400: '#303030',
    A700: '#616161'
  },
  // Complete background colors
  background: {
    default: '#FAFAFA',
    paper: '#fff',
    sidebar: '#6200ff',
    notification: '#6200ff',
    lightBlue: '#e6f3ff'
  },
  // Complete text colors
  text: {
    primary: '#0f172a',
    secondary: '#9095a4',
    disabled: '#B0B7C3',
    sidebar: '#fff'
  },
  // Complete divider color
  divider: '#E5EAF2'
});

export default palette;
