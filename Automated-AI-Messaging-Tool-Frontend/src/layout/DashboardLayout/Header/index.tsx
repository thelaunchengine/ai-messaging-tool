import { ReactNode, useMemo } from 'react';

// material-ui
import useMediaQuery from '@mui/material/useMediaQuery';
import AppBar, { AppBarProps } from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';

// project-imports
import AppBarStyled from './AppBarStyled';
import HeaderContent from './HeaderContent';

import { useGetMenuMaster } from 'api/menu';
import { DRAWER_WIDTH, MenuOrientation } from 'config';
import useConfig from 'hooks/useConfig';

// next
import { usePathname } from 'next/navigation';

// ==============================|| MAIN LAYOUT - HEADER ||============================== //

interface HeaderProps {
  onMenuClick?: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const downLG = useMediaQuery((theme) => theme.breakpoints.down('lg'));
  const pathname = usePathname();
  const isAdminRoute = pathname.startsWith('/admin');

  const { menuOrientation } = useConfig();
  const { menuMaster } = useGetMenuMaster();
  const drawerOpen = menuMaster.isDashboardDrawerOpened;

  const isHorizontal = menuOrientation === MenuOrientation.HORIZONTAL && !downLG;

  // header content
  const headerContent = useMemo(() => <HeaderContent onMenuClick={onMenuClick} />, [onMenuClick]);

  // common header
  const mainHeader: ReactNode = (
    <Toolbar sx={{ 
      px: { xs: 2, sm: 2.5, md: 4.5, lg: 8 },
      minHeight: 64,
      backgroundColor: '#fff',
      borderBottom: '1px solid #E5E7EB'
    }}>
      {headerContent}
    </Toolbar>
  );

  // app-bar params
  const appBar: AppBarProps = {
    position: 'fixed',
    elevation: 0,
    sx: {
      backgroundColor: '#fff',
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      zIndex: 1200,
      width: isHorizontal
        ? '100%'
        : { xs: '100%', lg: `calc(100% - ${DRAWER_WIDTH}px)` }
    }
  };

  return (
    <>
      {!downLG ? (
        <AppBarStyled open={drawerOpen} {...appBar}>
          {mainHeader}
        </AppBarStyled>
      ) : (
        <AppBar {...appBar}>{mainHeader}</AppBar>
      )}
    </>
  );
}
