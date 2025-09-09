'use client';

import { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import {
  Dashboard as DashboardIcon,
  Upload as UploadIcon,
  History as HistoryIcon,
  People,
  Analytics,
  Message
} from '@mui/icons-material';
import { DRAWER_WIDTH } from '../../config';

const userMenuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'List', icon: <UploadIcon />, path: '/file-upload' },
  { text: 'List Report', icon: <HistoryIcon />, path: '/history' }
];

const adminMenuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/admin/dashboard' },
  { text: 'Users', icon: <People />, path: '/admin/users' },
  { text: 'Reports', icon: <Analytics />, path: '/admin/reports' },
  { text: 'Messages', icon: <Message />, path: '/admin/messages' },
  { text: 'List History', icon: <HistoryIcon />, path: '/admin/history' }
];

export default function CustomSidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const { data: session, status } = useSession();
  const isAdminRoute = pathname.startsWith('/admin');
  const isAdmin = session?.user?.role === 'ADMIN' || session?.user?.role === 'admin';

  // Show admin menu if user is admin and on admin route, otherwise show user menu
  const menuList = (isAdmin && isAdminRoute) ? adminMenuItems : userMenuItems;

  return (
    <Box
      component="aside"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        position: 'fixed',
        left: 0,
        top: 0,
        height: '100vh',
        zIndex: 1200,
        backgroundColor: '#F8FAFC',
        borderRight: 'none',
        boxShadow: '0 2px 12px 0 rgba(80,112,251,0.04)'
      }}
    >
      {/* Header Section */}
      <Box
        component="header"
        sx={{
          p: 3,
          pb: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          borderBottom: '1px solid',
          borderColor: 'divider',
          mb: 2,
          backgroundColor: 'transparent'
        }}
      >
        <Box
          component="a"
          href={isAdmin && isAdminRoute ? "/admin/dashboard" : "/dashboard"}
          sx={{
            textDecoration: 'none',
            color: 'inherit',
            display: 'block',
            width: '100%'
          }}
        >
          <Typography
            variant="h6"
            sx={{
              fontWeight: 800,
              fontSize: '1.25rem',
              color: '#1A202C',
              letterSpacing: 0.5,
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            AI Messaging Tool
          </Typography>
        </Box>
      </Box>

      {/* Navigation Section */}
      <Box
        component="nav"
        sx={{
          flex: 1,
          overflowY: 'auto',
          px: 1
        }}
      >
        <List
          component="ul"
          sx={{
            mt: 2,
            p: 0,
            '& .MuiListItem-root': {
              mb: 0.5
            }
          }}
        >
          {menuList.map((item) => {
            const isActive = pathname === item.path;
            return (
              <ListItem
                key={item.text}
                component="li"
                disablePadding
                disableGutters
                sx={{
                  mb: 0.5,
                  listStyle: 'none'
                }}
              >
                <Paper
                  component="div"
                  elevation={0}
                  sx={{
                    width: '100%',
                    borderRadius: 2,
                    overflow: 'hidden',
                    backgroundColor: 'transparent'
                  }}
                >
                  <ListItemButton
                    component="button"
                    selected={isActive}
                    onClick={() => item.path && router.push(item.path)}
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
                      border: 'none',
                      outline: 'none',
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
                      },
                      '&:focus': {
                        outline: 'none'
                      }
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        color: isActive ? '#FFFFFF' : '#374151',
                        minWidth: 36,
                        fontSize: 22,
                        '& svg': {
                          color: isActive ? '#FFFFFF !important' : '#374151 !important',
                        }
                      }}
                    >
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
                </Paper>
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Box>
  );
} 