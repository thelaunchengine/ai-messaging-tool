'use client';

import { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import Badge from '@mui/material/Badge';
import TouchRipple from '@mui/material/ButtonBase/TouchRipple';
import {
  Dashboard as DashboardIcon,
  Upload as UploadIcon,
  History as HistoryIcon,
  People,
  Analytics,
  Message,
  BugReport
} from '@mui/icons-material';
import menuItems from '../../menu-items';
import Divider from '@mui/material/Divider';
import { DRAWER_WIDTH } from '../../config';

const userMenuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'List', icon: <UploadIcon />, path: '/file-upload' },
  { text: 'List Report', icon: <HistoryIcon />, path: '/history' }
];

const adminMenuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/admin/dashboard' },
  { text: 'Users', icon: <People />, path: '/admin/users' },
  { text: 'File Upload', icon: <UploadIcon />, path: '/admin/file-upload' },
  { text: 'Scraping', icon: <BugReport />, path: '/admin/scraping' },
  { text: 'Reports', icon: <Analytics />, path: '/admin/reports' },
  { text: 'Messages', icon: <Message />, path: '/admin/messages' },
  { text: 'List History', icon: <HistoryIcon />, path: '/admin/history' }
];

export default function DrawerComponent() {
  const router = useRouter();
  const pathname = usePathname();
  const { data: session, status } = useSession();
  const isAdminRoute = pathname.startsWith('/admin');
  const isAdmin = (session?.user as any)?.role === 'ADMIN' || (session?.user as any)?.role === 'admin';

  // Show admin menu if user is admin and on admin route, otherwise show user menu
  const menuList = (isAdmin && isAdminRoute) ? adminMenuItems : userMenuItems;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          borderRight: 'none',
          backgroundColor: '#F8FAFC',
          color: '#374151',
          boxShadow: '0 2px 12px 0 rgba(80,112,251,0.04)'
        }
      }}
    >
      <Box sx={{ p: 3, pb: 2, display: 'flex', alignItems: 'center', gap: 1, borderBottom: '1px solid', borderColor: 'divider', mb: 2 }}>
        <a href={isAdmin && isAdminRoute ? "/admin/dashboard" : "/dashboard"} style={{ textDecoration: 'none', color: 'inherit' }}>
          <Typography variant="h6" sx={{ fontWeight: 800, fontSize: '1.25rem', color: '#1A202C', letterSpacing: 0.5, cursor: 'pointer' }}>
            AI Messaging Tool
          </Typography>
        </a>
      </Box>
      <List sx={{ mt: 2 }}>
        {menuList.map((item) => {
          const isActive = pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding disableGutters sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={isActive}
                onClick={() => item.path && router.push(item.path)}
                TouchRippleProps={{ center: false }}
                sx={{
                  borderRadius: 2,
                  mx: 0.5,
                  my: 0.5,
                  minHeight: 44,
                  px: 2,
                  py: 1,
                  gap: 2,
                  bgcolor: isActive ? '#6100ff' : 'transparent',
                  color: isActive ? '#FFFFFF' : '#374151',
                  fontWeight: isActive ? 600 : 400,
                  width: 'calc(100% - 8px)',
                  '& .MuiListItemIcon-root': {
                    color: isActive ? '#FFFFFF' : '#374151',
                    '& svg': {
                      color: isActive ? '#FFFFFF !important' : '#374151 !important',
                    }
                  },
                  '&.Mui-selected': {
                    bgcolor: '#6100ff',
                    color: '#FFFFFF',
                    fontWeight: 600,
                    '& .MuiListItemIcon-root': { 
                      color: '#FFFFFF',
                      '& svg': {
                        color: '#FFFFFF !important',
                      }
                    }
                  },
                  '&:hover': {
                    bgcolor: '#F3F0FF',
                    color: '#6100ff',
                    '& .MuiListItemIcon-root': { 
                      color: '#6100ff',
                      '& svg': {
                        color: '#6100ff !important',
                      }
                    }
                  }
                }}
              >
                <ListItemIcon sx={{ 
                  color: isActive ? '#FFFFFF' : '#374151', 
                  minWidth: 36, 
                  fontSize: 22,
                  '& svg': {
                    color: isActive ? '#FFFFFF !important' : '#374151 !important',
                  }
                }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  sx={{
                    '& .MuiListItemText-primary': {
                      fontSize: '.85rem',
                      fontWeight: isActive ? 700 : 500,
                      letterSpacing: 0.2,
                      color: isActive ? '#FFFFFF' : '#374151'
                    }
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Drawer>
  );
}
