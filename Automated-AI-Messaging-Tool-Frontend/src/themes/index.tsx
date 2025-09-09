'use client';

import { ReactNode, useMemo } from 'react';

// material-ui
import { createTheme, ThemeOptions, ThemeProvider, Theme, TypographyVariantsOptions } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// project-imports
import { ThemeMode } from '../types/config';
import Palette from './palette';
import Typography from './typography';
import CustomShadows from './shadows';
import GlobalStyles from './GlobalStyles';
import { NextAppDirEmotionCacheProvider } from './emotionCache';
import componentsOverride from './components';

import { HEADER_HEIGHT } from 'config';
import useConfig from 'hooks/useConfig';
import getWindowScheme from 'utils/getWindowScheme';

// types
import { CustomShadowProps } from 'types/theme';

type ThemeCustomizationProps = {
  children: ReactNode;
};

// ==============================|| DEFAULT THEME - MAIN  ||============================== //

export default function ThemeCustomization({ children }: ThemeCustomizationProps) {
  const { themeDirection, mode, presetColor, fontFamily, themeContrast } = useConfig();
  let themeMode: any = mode;
  if (themeMode === ThemeMode.AUTO) {
    const autoMode = getWindowScheme();
    if (autoMode) {
      themeMode = ThemeMode.DARK;
    } else {
      themeMode = ThemeMode.LIGHT;
    }
  }

  const theme: Theme = useMemo<Theme>(() => Palette(themeMode), [themeMode]);

  const themeTypography = useMemo(() => Typography(themeMode, fontFamily, theme), [themeMode, fontFamily, theme]);
  const themeCustomShadows = useMemo(() => CustomShadows(themeMode, theme), [themeMode, theme]);

  const themeOptions: ThemeOptions = useMemo(
    () => ({
      direction: 'ltr',
      palette: theme.palette,
      mixins: {
        toolbar: {
          minHeight: '60px',
          paddingTop: '8px',
          paddingBottom: '8px'
        }
      },
      typography: themeTypography,
      customShadows: themeCustomShadows
    }),
    [theme, themeTypography, themeCustomShadows]
  );

  const themes = createTheme(themeOptions);
  themes.components = componentsOverride(themes);

  return (
    <NextAppDirEmotionCacheProvider options={{ key: 'mui' }}>
      <ThemeProvider theme={themes}>
        <CssBaseline enableColorScheme />
        <GlobalStyles />
        {children}
      </ThemeProvider>
    </NextAppDirEmotionCacheProvider>
  );
}
