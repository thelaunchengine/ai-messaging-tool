'use client';

import { lazy, ReactNode } from 'react';

// material-ui
import Container from '@mui/material/Container';
import Toolbar from '@mui/material/Toolbar';

// project-imports
import LayoutContent from './LayoutContent';
import { useGetMenuMaster } from 'api/menu';
import Loader from 'components/Loader';

const Header = lazy(() => import('./Header'));

// ==============================|| COMPONENT LAYOUT ||============================== //

interface Props {
  children: ReactNode;
}

export default function ComponentLayout({ children }: Props) {
  const { menuMasterLoading } = useGetMenuMaster();
  if (menuMasterLoading) return <Loader />;

  return (
    <Container maxWidth="xl" sx={{ px: { xs: 0, sm: 2.5 } }}>
      <Header />
      <Toolbar sx={{ mt: 2 }} />
      <LayoutContent>{children}</LayoutContent>
    </Container>
  );
}
