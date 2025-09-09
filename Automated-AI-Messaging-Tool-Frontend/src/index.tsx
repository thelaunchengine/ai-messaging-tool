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
  console.log('🎨 ThemeCustomization: Component rendering');
  
  const [themeMode] = useThemeMode();
  console.log('🎨 ThemeCustomization: Theme mode:', themeMode);

  const theme: Theme = useMemo<Theme>(() => {
    console.log('🎨 ThemeCustomization: useMemo running, creating theme with mode:', themeMode);
    const paletteTheme = Palette(themeMode);
    console.log('🎨 ThemeCustomization: Palette created:', paletteTheme);
    return paletteTheme;
  }, [themeMode]);

  console.log('🎨 ThemeCustomization: Final theme object:', theme);

  const themeOptions = useMemo<ThemeOptions>(() => {
    console.log('🎨 ThemeCustomization: Creating theme options');
    return {
      ...theme,
      shape: { borderRadius: 8 },
      spacing: 8,
    };
  }, [theme]);

  console.log('🎨 ThemeCustomization: Theme options created:', themeOptions);

  const themes = createTheme(themeOptions);
  console.log('🎨 ThemeCustomization: createTheme result:', themes);
  
  themes.components = componentsOverride(themes);
  console.log('🎨 ThemeCustomization: Components overridden');

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
