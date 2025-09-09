'use client';

// material-ui
import { Theme, alpha } from '@mui/material/styles';

// project-imports
import { ThemeMode } from '../types/config';

// types
import { CustomShadowProps } from 'types/theme';

// ==============================|| DEFAULT THEME - SHADOWS  ||============================== //

export default function CustomShadows(mode: ThemeMode): CustomShadowProps {
  const transparent = mode === ThemeMode.DARK ? 'rgba(255, 255, 255, 0.16)' : 'rgba(0, 0, 0, 0.16)';
  const transparent2 = mode === ThemeMode.DARK ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)';

  // Define color values directly
  const colors = {
    primary: '#2196F3',
    secondary: '#673AB7',
    warning: '#FF9800',
    success: '#4CAF50',
    error: '#F44336'
  };

  return {
    button: mode === ThemeMode.DARK ? `0 2px 0 rgb(0 0 0 / 5%)` : `0 2px #0000000b`,
    text: `0 -1px 0 rgb(0 0 0 / 12%)`,
    z1: `0 2px 8px 0 ${transparent}`,
    z4: `0 4px 16px 0 ${transparent}`,
    z8: `0 8px 16px 0 ${transparent}`,
    z12: `0 12px 24px -4px ${transparent}`,
    z16: `0 16px 32px -4px ${transparent}`,
    z20: `0 20px 40px -4px ${transparent}`,
    z24: `0 24px 48px 0 ${transparent}`,
    primary: `0 8px 16px 0 ${alpha(colors.primary, 0.24)}`,
    secondary: `0 8px 16px 0 ${alpha(colors.secondary, 0.24)}`,
    orange: `0 8px 16px 0 ${alpha(colors.warning, 0.24)}`,
    success: `0 8px 16px 0 ${alpha(colors.success, 0.24)}`,
    warning: `0 8px 16px 0 ${alpha(colors.warning, 0.24)}`,
    error: `0 8px 16px 0 ${alpha(colors.error, 0.24)}`,
    info: `0 8px 16px 0 ${colors.primary}14`,
    card: `0 0 2px 0 ${transparent2}, 0 8px 16px 0 ${transparent}`,
    dialog: `-40px 40px 80px 0 ${transparent}`,
    dropdown: `0 0 2px 0 ${transparent2}, 0 8px 16px 0 ${transparent}`,
    grey: `0 0 0 2px ${colors.secondary}14`,
    primaryButton: `0 14px 12px ${colors.primary}14`,
    secondaryButton: `0 14px 12px ${colors.secondary}14`,
    errorButton: `0 14px 12px ${colors.error}14`,
    warningButton: `0 14px 12px ${colors.warning}14`,
    infoButton: `0 14px 12px ${colors.primary}14`,
    successButton: `0 14px 12px ${colors.success}14`,
    greyButton: `0 14px 12px ${colors.secondary}14`
  };
}
