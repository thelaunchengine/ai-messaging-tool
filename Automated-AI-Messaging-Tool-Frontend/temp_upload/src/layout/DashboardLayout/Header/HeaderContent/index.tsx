import { useMemo } from 'react';

// material-ui
import { Theme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import Box from '@mui/material/Box';

// project-imports
import FullScreen from './FullScreen';
import Localization from './Localization';
import MegaMenuSection from './MegaMenuSection';
import Message from './Message';
import MobileSection from './MobileSection';
import Notification from './Notification';
import Profile from './Profile';
import Search from './Search';

import { MenuOrientation } from 'config';
import useConfig from 'hooks/useConfig';
import DrawerHeader from 'layout/DashboardLayout/Drawer/DrawerHeader';

// ==============================|| HEADER - CONTENT ||============================== //

export default function HeaderContent() {
  const { menuOrientation } = useConfig();

  const downLG = useMediaQuery((theme: Theme) => theme.breakpoints.down('lg'));

  const localization = useMemo(() => <Localization />, []);

  const megaMenu = useMemo(() => <MegaMenuSection />, []);

  return (
    <>
      {/* Removed DrawerHeader, MegaMenuSection, and Localization for a cleaner header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', flex: 1, gap: 2 }}>
        <Profile />
      </Box>
    </>
  );
}
