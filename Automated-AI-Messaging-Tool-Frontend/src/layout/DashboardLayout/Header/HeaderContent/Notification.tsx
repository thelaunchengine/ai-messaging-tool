import { useRef, useState } from 'react';

// material-ui
import useMediaQuery from '@mui/material/useMediaQuery';
import Badge from '@mui/material/Badge';
import CardContent from '@mui/material/CardContent';
import ClickAwayListener from '@mui/material/ClickAwayListener';
import Link from '@mui/material/Link';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Paper from '@mui/material/Paper';
import Popper from '@mui/material/Popper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

// project-imports
import Avatar from 'components/@extended/Avatar';
import IconButton from 'components/@extended/IconButton';
import Transitions from 'components/@extended/Transitions';
import MainCard from 'components/MainCard';
import SimpleBar from 'components/third-party/SimpleBar';

// assets
import { Gift, MessageText1, Notification, Setting2 } from '@wandersonalwes/iconsax-react';

const actionSX = {
  mt: '6px',
  ml: 1,
  top: 'auto',
  right: 'auto',
  alignSelf: 'flex-start',
  transform: 'none'
};

// ==============================|| HEADER CONTENT - NOTIFICATION ||============================== //

export default function NotificationPage() {
  const downMD = useMediaQuery((theme) => theme.breakpoints.down('md'));

  const anchorRef = useRef<any>(null);
  const [read] = useState(2);
  const [open, setOpen] = useState(false);
  const handleToggle = () => {
    setOpen((prevOpen) => !prevOpen);
  };

  const handleClose = (event: MouseEvent | TouchEvent) => {
    if (anchorRef.current && anchorRef.current.contains(event.target)) {
      return;
    }
    setOpen(false);
  };

  return (
    <Box sx={{ flexShrink: 0, ml: 0.5 }}>
      <IconButton
        color="secondary"
        variant="light"
        aria-label="open profile"
        ref={anchorRef}
        aria-controls={open ? 'profile-grow' : undefined}
        aria-haspopup="true"
        onClick={handleToggle}
        size="large"
        sx={{
          p: 1,
          color: '#374151',
          backgroundColor: open ? '#F3F4F6' : '#F9FAFB',
          border: '1px solid #E5E7EB',
          '&:hover': {
            backgroundColor: '#F3F4F6'
          }
        }}
      >
        <Badge badgeContent={read} color="success" sx={{ '& .MuiBadge-badge': { top: 2, right: 4 } }}>
          <Notification variant="Bold" />
        </Badge>
      </IconButton>
      <Popper
        placement={downMD ? 'bottom' : 'bottom-end'}
        open={open}
        anchorEl={anchorRef.current}
        role={undefined}
        transition
        disablePortal
        popperOptions={{ modifiers: [{ name: 'offset', options: { offset: [downMD ? -5 : 0, 9] } }] }}
      >
        {({ TransitionProps }) => (
          <Transitions type="grow" position={downMD ? 'top' : 'top-right'} in={open} {...TransitionProps}>
            <Paper sx={{ 
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
              borderRadius: 2,
              width: { xs: 320, sm: 420 },
              backgroundColor: '#fff',
              border: '1px solid #E5E7EB'
            }}>
              <ClickAwayListener onClickAway={handleClose}>
                <MainCard border={false} content={false}>
                  <CardContent>
                    <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography variant="h5" sx={{ color: '#111827', fontWeight: 600 }}>Notifications</Typography>
                      <Link href="#" variant="h6" sx={{ color: '#7B3FF2', textDecoration: 'none', fontWeight: 500 }}>
                        Mark all read
                      </Link>
                    </Stack>
                    <SimpleBar style={{ maxHeight: 'calc(100vh - 180px)' }}>
                      <List
                        component="nav"
                        sx={{
                          '& .MuiListItemButton-root': {
                            p: 1.5,
                            my: 1.5,
                            border: '1px solid #E5E7EB',
                            borderRadius: 1,
                            backgroundColor: '#F9FAFB',
                            '&:hover': { 
                              backgroundColor: '#F3F4F6',
                              borderColor: '#7B3FF2'
                            },
                            '& .MuiListItemSecondaryAction-root': { ...actionSX, position: 'relative' },
                            '&:hover .MuiAvatar-root': { backgroundColor: '#7B3FF2', color: '#fff' }
                          }
                        }}
                      >
                        <ListItem
                          component={ListItemButton}
                          secondaryAction={
                            <Typography variant="caption" noWrap>
                              3:00 AM
                            </Typography>
                          }
                        >
                          <ListItemAvatar>
                            <Avatar type="filled">
                              <Gift size={20} variant="Bold" />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={
                              <Typography variant="h6">
                                It&apos;s{' '}
                                <Typography component="span" variant="subtitle1">
                                  Cristina danny&apos;s
                                </Typography>{' '}
                                birthday today.
                              </Typography>
                            }
                            secondary="2 min ago"
                          />
                        </ListItem>

                        <ListItem
                          component={ListItemButton}
                          secondaryAction={
                            <Typography variant="caption" noWrap>
                              6:00 PM
                            </Typography>
                          }
                        >
                          <ListItemAvatar>
                            <Avatar type="outlined">
                              <MessageText1 size={20} variant="Bold" />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={
                              <Typography variant="h6">
                                <Typography component="span" variant="subtitle1">
                                  Aida Burg
                                </Typography>{' '}
                                commented your post.
                              </Typography>
                            }
                            secondary="5 August"
                          />
                        </ListItem>

                        <ListItem
                          component={ListItemButton}
                          secondaryAction={
                            <Typography variant="caption" noWrap>
                              2:45 PM
                            </Typography>
                          }
                        >
                          <ListItemAvatar>
                            <Avatar>
                              <Setting2 size={20} variant="Bold" />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={
                              <Typography variant="h6">
                                Your Profile is Complete &nbsp;
                                <Typography component="span" variant="subtitle1">
                                  60%
                                </Typography>{' '}
                              </Typography>
                            }
                            secondary="7 hours ago"
                          />
                        </ListItem>

                        <ListItem
                          component={ListItemButton}
                          secondaryAction={
                            <Typography variant="caption" noWrap>
                              9:10 PM
                            </Typography>
                          }
                        >
                          <ListItemAvatar>
                            <Avatar type="combined">C</Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={
                              <Typography variant="h6">
                                <Typography component="span" variant="subtitle1">
                                  Cristina Danny
                                </Typography>{' '}
                                invited to join{' '}
                                <Typography component="span" variant="subtitle1">
                                  Meeting.
                                </Typography>
                              </Typography>
                            }
                            secondary="Daily scrum meeting time"
                          />
                        </ListItem>
                      </List>
                    </SimpleBar>
                    <Stack direction="row" sx={{ justifyContent: 'center', mt: 1.5 }}>
                      <Link href="#" variant="h6" color="primary">
                        View all
                      </Link>
                    </Stack>
                  </CardContent>
                </MainCard>
              </ClickAwayListener>
            </Paper>
          </Transitions>
        )}
      </Popper>
    </Box>
  );
}
