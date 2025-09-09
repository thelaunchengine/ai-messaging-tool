'use client';

import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import DashboardLayout from '../../layout/DashboardLayout';
import AuthGuard from '../../utils/route-guard/AuthGuard';

export default function DashboardLayoutWrapper({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // During SSR and initial client render, return a minimal layout
  if (!mounted) {
    return (
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <Box component="main" sx={{ flexGrow: 1 }}>
          {children}
        </Box>
      </Box>
    );
  }

  // After hydration, return the full layout
  return (
    <DashboardLayout>
      {children}
    </DashboardLayout>
  );
}
