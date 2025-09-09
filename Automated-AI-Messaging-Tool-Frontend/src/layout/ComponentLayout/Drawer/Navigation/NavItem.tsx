'use client';

import { useEffect } from 'react';

// next
import Link from 'next/link';

// material-ui
import useMediaQuery from '@mui/material/useMediaQuery';
import Avatar from '@mui/material/Avatar';
import Chip from '@mui/material/Chip';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';

// project imports
import { handlerActiveComponent, handlerComponentDrawer, useGetMenuMaster } from 'api/menu';

// third-party
import { FormattedMessage } from 'react-intl';

// types
import { LinkTarget, NavItemType } from 'types/menu';

// ==============================|| NAVIGATION - LIST ITEM ||============================== //

interface Props {
  item: NavItemType;
}

export default function NavItem({ item }: Props) {
  const { menuMaster } = useGetMenuMaster();
  const openComponent = menuMaster.openedComponent;
  const downMD = useMediaQuery((theme) => theme.breakpoints.down('md'));

  let itemTarget: LinkTarget = '_self';
  if (item.target) {
    itemTarget = '_blank';
  }

  const itemHandler = (id: string) => {
    handlerActiveComponent(id);
    if (downMD) handlerComponentDrawer(false);
  };

  // active menu item on page load
  useEffect(() => {
    const currentIndex = document.location.pathname
      .toString()
      .split('/')
      .findIndex((id) => id === item.id);
    if (currentIndex > -1) {
      handlerActiveComponent(item.id!);
    }
    // eslint-disable-next-line
  }, []);

  const isSelectedItem = openComponent === item.id;

  return (
    <ListItemButton
      component={Link}
      href={item.url!}
      target={itemTarget}
      disabled={item.disabled}
      onClick={() => itemHandler(item.id!)}
      selected={isSelectedItem}
      sx={{
        pl: 2,
        py: 0.75,
        mb: 0.25,
        borderRadius: 2,
        alignItems: 'center',
        backgroundColor: isSelectedItem ? '#E8EFFF' : 'transparent',
        '&.Mui-selected': {
          backgroundColor: '#E8EFFF',
          '& .MuiTypography-root': {
            color: '#7B3FF2',
            fontWeight: 600
          },
          '& .MuiListItemIcon-root': {
            color: '#7B3FF2'
          }
        },
        '&:hover': {
          backgroundColor: '#E8EFFF',
        },
        '& .MuiListItemIcon-root': {
          color: isSelectedItem ? '#7B3FF2' : '#374151',
          minWidth: 28
        },
        '& .MuiTypography-root': {
          color: isSelectedItem ? '#7B3FF2' : '#374151',
          fontWeight: isSelectedItem ? 600 : 500,
          fontSize: '0.95rem',
          letterSpacing: 0.2
        }
      }}
    >
      <ListItemText
        primary={
          <Typography
            variant="h6"
            sx={{
              color: isSelectedItem ? '#7B3FF2' : '#374151',
              fontWeight: isSelectedItem ? 600 : 500,
              fontSize: '0.95rem',
              letterSpacing: 0.2
            }}
          >
            <FormattedMessage id={item.title as string} />
          </Typography>
        }
      />
      {item.chip && (
        <Chip
          sx={{
            backgroundColor: '#7B3FF2',
            color: '#fff',
            fontWeight: 700,
            fontSize: 12,
            borderRadius: 8,
            px: 1.5
          }}
          label={item.chip.label}
          size="small"
        />
      )}
    </ListItemButton>
  );
}
