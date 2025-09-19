'use client';

import { useEffect, ReactNode, useState } from 'react';

// material-ui
import useMediaQuery from '@mui/material/useMediaQuery';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Links from '@mui/material/Link';
import Toolbar from '@mui/material/Toolbar';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';

// project-imports
import CustomSidebar from 'components/CustomSidebar';
import Header from './Header';
import Footer from './Footer';
import HorizontalBar from './Drawer/HorizontalBar';
import Breadcrumbs from 'components/@extended/Breadcrumbs';
import Loader from 'components/Loader';
import AddCustomer from 'sections/apps/customer/AddCustomer';
import { useIspValue } from 'hooks/useIspValue';

import { handlerDrawerOpen, useGetMenuMaster } from 'api/menu';
import { DRAWER_WIDTH, MenuOrientation } from 'config';
import useConfig from 'hooks/useConfig';
import { usePathname } from 'next/navigation';

// ==============================|| MAIN LAYOUT ||============================== //

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { menuMasterLoading } = useGetMenuMaster();
  const downXL = useMediaQuery((theme) => theme.breakpoints.down('xl'));
  const downLG = useMediaQuery((theme) => theme.breakpoints.down('lg'));
  const downMD = useMediaQuery((theme) => theme.breakpoints.down('md'));

  const { container, miniDrawer, menuOrientation } = useConfig();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isHorizontal = menuOrientation === MenuOrientation.HORIZONTAL && !downLG;

  const ispValueAvailable = useIspValue();

  const url = ispValueAvailable ? 'https://1.envato.market/jrEAbP' : 'https://1.envato.market/zNkqj6';
  const pathname = usePathname();
  const isAdminRoute = pathname.startsWith('/admin');

  // Handle mobile drawer toggle
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // set media wise responsive drawer
  useEffect(() => {
    if (!miniDrawer) {
      handlerDrawerOpen(!downXL);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [downXL]);

  // Add body class for admin routes
  useEffect(() => {
    if (isAdminRoute) {
      document.body.classList.add('admin-route');
    } else {
      document.body.classList.remove('admin-route');
    }

    return () => {
      document.body.classList.remove('admin-route');
    };
  }, [isAdminRoute]);

  if (menuMasterLoading) return <Loader />;

  return (
    <Box sx={{ display: 'flex', width: '100%' }}>
      <Header onMenuClick={handleDrawerToggle} />
      
      {/* Desktop Sidebar */}
      {!isHorizontal && !downMD && <CustomSidebar />}
      
      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
            backgroundColor: '#F8FAFC',
            borderRight: 'none',
            boxShadow: '0 2px 12px 0 rgba(80,112,251,0.04)'
          },
        }}
      >
        <CustomSidebar onClose={handleDrawerToggle} />
      </Drawer>

      {/* Horizontal Bar for large screens */}
      {isHorizontal && <HorizontalBar />}

      <Box 
        component="main" 
        className={isAdminRoute ? 'admin-main-content' : ''}
        sx={{ 
          width: { xs: '100%', md: `calc(100% - ${DRAWER_WIDTH}px)` }, 
          flexGrow: 1, 
          p: { xs: 1, sm: 3 },
          backgroundColor: '#F9FAFB',
          minHeight: '100vh',
          marginLeft: { xs: 0, md: `${DRAWER_WIDTH}px` },
          // Admin-specific styling
          ...(isAdminRoute && {
            '&.admin-main-content': {
              marginLeft: { xs: 0, md: '115px !important' }
            }
          })
        }}
      >
        <Toolbar sx={{ mt: isHorizontal ? 8 : 'inherit', mb: isHorizontal ? 2 : 'inherit' }} />
        <Container
          maxWidth={container && !downXL ? 'xl' : false}
          sx={{
            ...(container && !downXL && { px: { xs: 0, sm: 3 } }),
            position: 'relative',
            minHeight: 'calc(100vh - 124px)',
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#fff',
            borderRadius: 2,
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
            border: '1px solid #E5E7EB'
          }}
        >
          <Breadcrumbs />
          {children}
          <Footer />
        </Container>
      </Box>
      <AddCustomer />
    </Box>
  );
}
