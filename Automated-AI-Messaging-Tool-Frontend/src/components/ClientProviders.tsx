'use client';

import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { SessionProvider } from 'next-auth/react';
import ThemeCustomization from '../themes';
import Locales from './Locales';
import { ConfigProvider } from '../contexts/ConfigContext';
import ErrorBoundary from './ErrorBoundary';
import GlobalErrorHandler from './GlobalErrorHandler';

interface ClientProvidersProps {
  children: React.ReactNode;
}

export default function ClientProviders({ children }: ClientProvidersProps) {
  return (
    <ErrorBoundary>
      <GlobalErrorHandler>
        <SessionProvider>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <ConfigProvider>
              <ThemeCustomization>
                <Locales>
                  <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
                    <main style={{ flex: 1 }}>{children}</main>
                  </div>
                </Locales>
              </ThemeCustomization>
            </ConfigProvider>
          </LocalizationProvider>
        </SessionProvider>
      </GlobalErrorHandler>
    </ErrorBoundary>
  );
} 