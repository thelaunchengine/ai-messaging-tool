// material-ui
import { styled, Theme, CSSObject } from '@mui/material/styles';
import Drawer from '@mui/material/Drawer';

// project-imports
import { DRAWER_WIDTH, MINI_DRAWER_WIDTH } from 'config';

const openedMixin = (theme: Theme): CSSObject => ({
  backgroundColor: '#7B3FF2', // Purple background for sidebar
  width: DRAWER_WIDTH,
  borderRight: 'none', // Remove border
  boxShadow: 'none',
  overflowX: 'hidden',

  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen
  })
});

const closedMixin = (theme: Theme): CSSObject => ({
  overflow: 'hidden',
  backgroundColor: '#7B3FF2', // Purple background for sidebar

  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen
  }),

  overflowX: 'hidden',
  width: MINI_DRAWER_WIDTH,
  borderRight: 'none',
  boxShadow: 'none'
});

// ==============================|| DRAWER - MINI STYLED ||============================== //

const MiniDrawerStyled = styled(Drawer, { shouldForwardProp: (prop) => prop !== 'open' })(({ theme, open }) => ({
  width: DRAWER_WIDTH,
  flexShrink: 0,
  whiteSpace: 'nowrap',
  boxSizing: 'border-box',
  ...(open && {
    ...openedMixin(theme),
    '& .MuiDrawer-paper': openedMixin(theme)
  }),
  ...(!open && {
    ...closedMixin(theme),
    '& .MuiDrawer-paper': closedMixin(theme)
  })
}));

export default MiniDrawerStyled;
