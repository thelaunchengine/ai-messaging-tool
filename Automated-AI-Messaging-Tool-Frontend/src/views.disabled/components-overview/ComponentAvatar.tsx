'use client';

import { useState } from 'react';

// material-ui
import AvatarGroup from '@mui/material/AvatarGroup';
import Badge from '@mui/material/Badge';
import CardMedia from '@mui/material/CardMedia';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

// project-imports
import Avatar from 'components/@extended/Avatar';
import ComponentHeader from 'components/cards/ComponentHeader';
import MainCard from 'components/MainCard';
import { GRID_COMMON_SPACING } from 'config';

import ComponentWrapper from 'sections/components-overview/ComponentWrapper';

// assets
import { Add, Coin, InfoCircle, Profile, Setting2, Sms, TickCircle, Trash, Warning2 } from '@wandersonalwes/iconsax-react';

const avatarImage = '/assets/images/users';

// ==============================|| COMPONENTS - AVATAR ||============================== //

export default function ComponentAvatar() {
  const [open, setOpen] = useState<boolean>(false);
  const [show, setShow] = useState<boolean>(false);

  const basicAvatarCodeString = `<Avatar alt="Basic"><Profile variant="Bold" /></Avatar>`;

  const imageAvatarCodeString = `<Avatar alt="Avatar 1" src={'${avatarImage}/avatar-1.png'} />
<Avatar alt="Avatar 2" src={'${avatarImage}/avatar-2.png'} />
<Avatar alt="Avatar 3" src={'${avatarImage}/avatar-3.png'} />
<Avatar alt="Avatar 4" src={'${avatarImage}/avatar-4.png'} />`;

  const vectorAvatarCodeString = `<Avatar><Image alt="Natacha" src={'${avatarImage}/vector-1.png'} height={40} width={40} /></Avatar>
<Avatar><Image alt="Natacha" src={'${avatarImage}/vector-2.png'} height={40} width={40} /></Avatar>
<Avatar><Image alt="Natacha" src={'${avatarImage}/vector-3.png'} height={40} width={40} /></Avatar>
<Avatar><Image alt="Natacha" src={'${avatarImage}/vector-4.png'} height={40} width={40} /></Avatar>`;

  const letterAvatarCodeString = `<Avatar alt="Natacha" size="sm">U</Avatar>
<Avatar color="error" alt="Natacha" size="sm">UI</Avatar>
<Avatar color="error" type="filled" alt="Natacha" size="sm">A</Avatar>`;

  const variantsAvatarCodeString = `<Avatar alt="Natacha"><Profile variant="Bold" /></Avatar>
<Avatar alt="Natacha" variant="rounded" type="combined" variant="Bold"><Profile /></Avatar>
<Avatar alt="Natacha" variant="square" type="filled"><Profile /></Avatar>
<Avatar alt="Natacha">U</Avatar>
<Avatar alt="Natacha" variant="rounded" type="combined">U</Avatar>
<Avatar alt="Natacha" variant="square" type="filled">U</Avatar>`;

  const outlinedAvatarCodeString = `<Avatar alt="Natacha" type="outlined"><Profile variant="Bold" /></Avatar>
<Avatar alt="Natacha" variant="rounded" type="outlined"><Profile variant="Bold" /></Avatar>
<Avatar alt="Natacha" variant="square" type="outlined"><Profile variant="Bold" /></Avatar>
<Avatar alt="Natacha" type="outlined">U</Avatar>
<Avatar alt="Natacha" variant="rounded" type="outlined">U</Avatar>
<Avatar alt="Natacha" variant="square" type="outlined">U</Avatar>`;

  const iconAvatarCodeString = `<Avatar alt="Natacha" size="sm" type="filled"><Profile /></Avatar>
<Avatar alt="Natacha" size="sm" type="filled" color="success"><SearchZoomIn /></Avatar>
<Avatar alt="Natacha" size="sm" type="filled" color="error"><SearchZoomOut1 /></Avatar>
<Avatar alt="Natacha" size="sm"><Add /></Avatar>`;

  const groupAvatarCodeString = `<AvatarGroup max={4}>
  <Avatar alt="Trevor Henderson" src={'${avatarImage}/avatar-5.png'} />
  <Avatar alt="Jone Doe" src={'${avatarImage}/avatar-6.png'} />
  <Avatar alt="Lein Ket" src={'${avatarImage}/avatar-7.png'} />
  <Avatar alt="Stebin Ben" src={'${avatarImage}/avatar-8.png'} />
  <Avatar alt="Wungh Tend" src={'${avatarImage}/avatar-9.png'} />
  <Avatar alt="Trevor Das" src={'${avatarImage}/avatar-10.png'} />
</AvatarGroup>
<Box sx={{ width: 186 }}>
  <Tooltip
    open={show}
    placement="top-end"
    title={
      <AvatarGroup max={10}>
        <Avatar alt="Trevor Henderson" src={'${avatarImage}/avatar-5.png'} />
        <Avatar alt="Jone Doe" src={'${avatarImage}/avatar-6.png'} />
        <Avatar alt="Lein Ket" src={'${avatarImage}/avatar-7.png'} />
        <Avatar alt="Stebin Ben" src={'${avatarImage}/avatar-8.png'} />
        <Avatar alt="Wungh Tend" src={'${avatarImage}/avatar-9.png'} />
        <Avatar alt="Trevor Das" src={'${avatarImage}/avatar-10.png'} />
      </AvatarGroup>
    }
  >
    <AvatarGroup
      sx={{ '& .MuiAvatarGroup-avatar': { bgcolor: 'primary.main', cursor: 'pointer' } }}
      componentsProps={{
        additionalAvatar: {
          onMouseEnter: () => {
            setShow(true);
          },
          onMouseLeave: () => {
            setShow(false);
          }
        }
      }}
    >
      <Avatar alt="Remy Sharp" src={'${avatarImage}/avatar-1.png'} />
      <Avatar alt="Travis Howard" src={'${avatarImage}/avatar-2.png'} />
      <Avatar alt="Cindy Baker" src={'${avatarImage}/avatar-3.png'} />
      <Avatar alt="Agnes Walker" src={'${avatarImage}/avatar-4.png'} />
      <Avatar alt="Trevor Henderson" src={'${avatarImage}/avatar-5.png'} />
      <Avatar alt="Jone Doe" src={'${avatarImage}/avatar-6.png'} />
      <Avatar alt="Lein Ket" src={'${avatarImage}/avatar-7.png'} />
      <Avatar alt="Stebin Ben" src={'${avatarImage}/avatar-8.png'} />
      <Avatar alt="Wungh Tend" src={'${avatarImage}/avatar-9.png'} />
      <Avatar alt="Trevor Das" src={'${avatarImage}/avatar-10.png'} />
    </AvatarGroup>
  </Tooltip>
</Box>
<Box sx={{ width: 222 }}>
  <Tooltip
    open={open}
    placement="top-end"
    title={
      <AvatarGroup max={10}>
        <Avatar alt="Jone Doe" src={'${avatarImage}/avatar-6.png'} />
        <Avatar alt="Lein Ket" src={'${avatarImage}/avatar-7.png'} />
        <Avatar alt="Stebin Ben" src={'${avatarImage}/avatar-8.png'} />
        <Avatar alt="Wungh Tend" src={'${avatarImage}/avatar-9.png'} />
        <Avatar alt="Trevor Das" src={'${avatarImage}/avatar-10.png'} />
      </AvatarGroup>
    }
  >
    <AvatarGroup
      max={6}
      sx={{ '& .MuiAvatarGroup-avatar': { bgcolor: 'primary.main', cursor: 'pointer' } }}
      componentsProps={{
        additionalAvatar: {
          onClick: () => {
            setOpen(!open);
          }
        }
      }}
    >
      <Avatar alt="Remy Sharp" src={'${avatarImage}/avatar-1.png'} />
      <Avatar alt="Travis Howard" src={'${avatarImage}/avatar-2.png'} />
      <Avatar alt="Cindy Baker" src={'${avatarImage}/avatar-3.png'} />
      <Avatar alt="Agnes Walker" src={'${avatarImage}/avatar-4.png'} />
      <Avatar alt="Trevor Henderson" src={'${avatarImage}/avatar-5.png'} />
      <Avatar alt="Jone Doe" src={'${avatarImage}/avatar-6.png'} />
      <Avatar alt="Lein Ket" src={'${avatarImage}/avatar-7.png'} />
      <Avatar alt="Stebin Ben" src={'${avatarImage}/avatar-8.png'} />
      <Avatar alt="Wungh Tend" src={'${avatarImage}/avatar-9.png'} />
      <Avatar alt="Trevor Das" src={'${avatarImage}/avatar-10.png'} />
    </AvatarGroup>
  </Tooltip>
</Box>`;

  const badgeAvatarCodeString = `<Badge badgeContent={4} color="error" overlap="circular">
  <Avatar alt="Natacha" type="filled" src={'${avatarImage}/avatar-6.png'} />
</Badge>
<Badge color="error" overlap="circular" variant="dot">
  <Avatar alt="Natacha" color="secondary" type="filled">
    <Profile />
  </Avatar>
</Badge>
<Badge color="error" overlap="circular" variant="dot">
  <Avatar alt="Natacha" type="filled" src={'${avatarImage}/avatar-2.png'} />
</Badge>
<Badge color="error" overlap="circular" variant="dot">
  <Avatar alt="Natacha" type="outlined">
    U
  </Avatar>
</Badge>
<Badge color="error" overlap="circular" variant="dot">
  <Avatar>
    <Image alt="Natacha" src={'${avatarImage}/vector-2.png'} width={40} height={40} />
  </Avatar>
</Badge>
<Badge color="success" variant="dot">
  <Avatar alt="Natacha" variant="rounded" type="filled" src={'${avatarImage}/avatar-1.png'} />
</Badge>
<Badge
  overlap="circular"
  anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
  badgeContent={<Avatar size="badge" alt="Remy Sharp" src={'${avatarImage}/avatar-6.png'} />}
>
  <Avatar alt="Travis Howard" src={'${avatarImage}/avatar-1.png'} />
</Badge>`;

  const sizesAvatarCodeString = `<Avatar size="xs" alt="Avatar 1" src={'${avatarImage}/avatar-1.png'} />
<Avatar size="xl" alt="Avatar 5" src={'${avatarImage}/avatar-5.png'} />
<Avatar size="lg" alt="Avatar 4" src={'${avatarImage}/avatar-4.png'} />
<Avatar size="md" alt="Avatar 3" src={'${avatarImage}/avatar-3.png'} />
<Avatar size="sm" alt="Avatar 2" src={'${avatarImage}/avatar-2.png'} />`;

  const colorsAvatarCodeString = `<Avatar alt="Basic" type="filled"><Profile variant="Bold" /></Avatar>
<Avatar alt="Basic" type="filled" color="error"><Trash variant="Bold" /></Avatar>
<Avatar alt="Basic" type="filled" color="info"><InfoCircle variant="Bold" /></Avatar>
<Avatar alt="Basic" type="filled" color="warning"><Warning2 variant="Bold" /></Avatar>
<Avatar alt="Basic" type="filled" color="success"><TickCircle variant="Bold" /></Avatar>
<Avatar alt="Basic" type="filled" color="secondary"><Coin variant="Bold" /></Avatar>`;

  const fallbacksAvatarCodeString = `<Avatar alt="Remy Sharp" src="/broken-image.jpg" color="error" type="filled">B</Avatar>
<Avatar src="/broken-image.jpg" color="error" />
<Avatar alt="Remy Sharp" src="/broken-image.jpg" color="error" type="outlined" />`;

  return (
    <>
      <ComponentHeader
        title="Avatar"
        caption="Avatars are found throughout material design with uses in everything from tables to dialog menus."
        directory="src/pages/components-overview/avatars"
        link="https://mui.com/material-ui/react-avatar/"
      />
      <ComponentWrapper>
        <Grid container spacing={GRID_COMMON_SPACING}>
          <Grid size={{ xs: 12, lg: 6 }}>
            <Stack sx={{ gap: GRID_COMMON_SPACING }}>
              <MainCard title="Basic" codeHighlight codeString={basicAvatarCodeString}>
                <Avatar alt="Basic">
                  <Profile variant="Bold" />
                </Avatar>
              </MainCard>
              <MainCard title="Vector" codeString={vectorAvatarCodeString}>
                <Grid container spacing={1}>
                  <Grid>
                    <Avatar>
                      <CardMedia component="img" sx={{ height: 40 }} alt="Natacha" src={`${avatarImage}/vector-1.png`} />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar>
                      <CardMedia component="img" sx={{ height: 40 }} alt="Natacha" src={`${avatarImage}/vector-2.png`} />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar>
                      <CardMedia component="img" sx={{ height: 40 }} alt="Natacha" src={`${avatarImage}/vector-3.png`} />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar>
                      <CardMedia component="img" sx={{ height: 40 }} alt="Natacha" src={`${avatarImage}/vector-4.png`} />
                    </Avatar>
                  </Grid>
                </Grid>
              </MainCard>
              <MainCard title="Variants" codeString={variantsAvatarCodeString}>
                <Grid container spacing={1}>
                  <Grid>
                    <Avatar alt="Natacha">
                      <Profile variant="Bold" />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" variant="rounded" type="combined">
                      <Profile variant="Bold" />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" variant="square" type="filled">
                      <Profile />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha">U</Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" variant="rounded" type="combined">
                      U
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" variant="square" type="filled">
                      U
                    </Avatar>
                  </Grid>
                </Grid>
              </MainCard>
              <MainCard title="Icon" codeString={iconAvatarCodeString}>
                <Grid container spacing={1}>
                  <Grid>
                    <Avatar alt="Natacha" size="sm" type="filled">
                      <Profile variant="Bold" />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" size="sm" type="filled" color="success">
                      <Sms variant="Bold" />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" size="sm" type="filled" color="error">
                      <Setting2 variant="Bold" />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" size="sm">
                      <Add />
                    </Avatar>
                  </Grid>
                </Grid>
              </MainCard>
              <MainCard title="With Badge" codeString={badgeAvatarCodeString}>
                <Grid container spacing={1}>
                  <Grid>
                    <Badge badgeContent={4} color="error" overlap="circular">
                      <Avatar alt="Natacha" type="filled" src={`${avatarImage}/avatar-6.png`} />
                    </Badge>
                  </Grid>
                  <Grid>
                    <Badge color="error" overlap="circular" variant="dot">
                      <Avatar alt="Natacha" color="secondary" type="filled">
                        <Profile />
                      </Avatar>
                    </Badge>
                  </Grid>
                  <Grid>
                    <Badge color="error" overlap="circular" variant="dot">
                      <Avatar alt="Natacha" type="filled" src={`${avatarImage}/avatar-2.png`} />
                    </Badge>
                  </Grid>
                  <Grid>
                    <Badge color="error" overlap="circular" variant="dot">
                      <Avatar alt="Natacha" type="outlined">
                        U
                      </Avatar>
                    </Badge>
                  </Grid>
                  <Grid>
                    <Badge color="error" overlap="circular" variant="dot">
                      <Avatar>
                        <CardMedia component="img" alt="Natacha" src={`${avatarImage}/vector-2.png`} sx={{ width: 40 }} />
                      </Avatar>
                    </Badge>
                  </Grid>
                  <Grid>
                    <Badge color="success" variant="dot">
                      <Avatar alt="Natacha" variant="rounded" type="filled" src={`${avatarImage}/avatar-1.png`} />
                    </Badge>
                  </Grid>
                  <Grid>
                    <Badge
                      overlap="circular"
                      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                      badgeContent={<Avatar size="badge" alt="Remy Sharp" src={`${avatarImage}/avatar-6.png`} />}
                    >
                      <Avatar alt="Travis Howard" src={`${avatarImage}/avatar-1.png`} />
                    </Badge>
                  </Grid>
                </Grid>
              </MainCard>
              <MainCard title="Image" codeString={imageAvatarCodeString}>
                <Grid container spacing={1}>
                  <Grid>
                    <Avatar alt="Avatar 1" src={`${avatarImage}/avatar-1.png`} />
                  </Grid>
                  <Grid>
                    <Avatar alt="Avatar 2" src={`${avatarImage}/avatar-2.png`} />
                  </Grid>
                  <Grid>
                    <Avatar alt="Avatar 3" src={`${avatarImage}/avatar-3.png`} />
                  </Grid>
                  <Grid>
                    <Avatar alt="Avatar 4" src={`${avatarImage}/avatar-4.png`} />
                  </Grid>
                </Grid>
              </MainCard>
              <MainCard title="Colors" codeString={colorsAvatarCodeString}>
                <Grid container spacing={1}>
                  <Grid>
                    <Avatar alt="Basic" type="filled">
                      <Profile />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Basic" type="filled" color="secondary">
                      <Coin />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Basic" type="filled" color="success">
                      <TickCircle />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Basic" type="filled" color="warning">
                      <Warning2 />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Basic" type="filled" color="info">
                      <InfoCircle />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Basic" type="filled" color="error">
                      <Trash />
                    </Avatar>
                  </Grid>
                </Grid>
              </MainCard>
            </Stack>
          </Grid>
          <Grid size={{ xs: 12, lg: 6 }}>
            <Stack sx={{ gap: GRID_COMMON_SPACING }}>
              <MainCard title="Letter" codeString={letterAvatarCodeString}>
                <Grid container spacing={1}>
                  <Grid>
                    <Avatar alt="Natacha" size="sm">
                      U
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar color="error" alt="Natacha" size="sm">
                      UI
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar color="error" type="filled" alt="Natacha" size="sm">
                      A
                    </Avatar>
                  </Grid>
                </Grid>
              </MainCard>
              <MainCard title="Outlined" codeString={outlinedAvatarCodeString}>
                <Grid container spacing={1}>
                  <Grid>
                    <Avatar alt="Natacha" type="outlined">
                      <Profile variant="Bold" />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" variant="rounded" type="outlined">
                      <Profile variant="Bold" />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" variant="square" type="outlined">
                      <Profile variant="Bold" />
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" type="outlined">
                      U
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" variant="rounded" type="outlined">
                      U
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Natacha" variant="square" type="outlined">
                      U
                    </Avatar>
                  </Grid>
                </Grid>
              </MainCard>
              <MainCard title="Avatar Group" codeString={groupAvatarCodeString}>
                <Stack sx={{ gap: 2 }}>
                  <Typography variant="subtitle1">Default</Typography>
                  <Box sx={{ width: 148 }}>
                    <AvatarGroup max={4}>
                      <Avatar alt="Trevor Henderson" src={`${avatarImage}/avatar-5.png`} />
                      <Avatar alt="Jone Doe" src={`${avatarImage}/avatar-6.png`} />
                      <Avatar alt="Lein Ket" src={`${avatarImage}/avatar-7.png`} />
                      <Avatar alt="Stebin Ben" src={`${avatarImage}/avatar-8.png`} />
                      <Avatar alt="Wungh Tend" src={`${avatarImage}/avatar-9.png`} />
                      <Avatar alt="Trevor Das" src={`${avatarImage}/avatar-10.png`} />
                    </AvatarGroup>
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle1">On Hover</Typography>
                  <Box sx={{ width: 186 }}>
                    <Tooltip
                      open={show}
                      placement="top-end"
                      title={
                        <AvatarGroup max={10}>
                          <Avatar alt="Trevor Henderson" src={`${avatarImage}/avatar-5.png`} />
                          <Avatar alt="Jone Doe" src={`${avatarImage}/avatar-6.png`} />
                          <Avatar alt="Lein Ket" src={`${avatarImage}/avatar-7.png`} />
                          <Avatar alt="Stebin Ben" src={`${avatarImage}/avatar-8.png`} />
                          <Avatar alt="Wungh Tend" src={`${avatarImage}/avatar-9.png`} />
                          <Avatar alt="Trevor Das" src={`${avatarImage}/avatar-10.png`} />
                        </AvatarGroup>
                      }
                    >
                      <AvatarGroup
                        sx={{ '& .MuiAvatarGroup-avatar': { bgcolor: 'primary.main', cursor: 'pointer' } }}
                        slotProps={{
                          surplus: {
                            onMouseEnter: () => {
                              setShow(true);
                            },
                            onMouseLeave: () => {
                              setShow(false);
                            }
                          }
                        }}
                      >
                        <Avatar alt="Remy Sharp" src={`${avatarImage}/avatar-1.png`} />
                        <Avatar alt="Travis Howard" src={`${avatarImage}/avatar-2.png`} />
                        <Avatar alt="Cindy Baker" src={`${avatarImage}/avatar-3.png`} />
                        <Avatar alt="Agnes Walker" src={`${avatarImage}/avatar-4.png`} />
                        <Avatar alt="Trevor Henderson" src={`${avatarImage}/avatar-5.png`} />
                        <Avatar alt="Jone Doe" src={`${avatarImage}/avatar-6.png`} />
                        <Avatar alt="Lein Ket" src={`${avatarImage}/avatar-7.png`} />
                        <Avatar alt="Stebin Ben" src={`${avatarImage}/avatar-8.png`} />
                        <Avatar alt="Wungh Tend" src={`${avatarImage}/avatar-9.png`} />
                        <Avatar alt="Trevor Das" src={`${avatarImage}/avatar-10.png`} />
                      </AvatarGroup>
                    </Tooltip>
                  </Box>
                </Stack>
                <Divider sx={{ my: 2 }} />
                <Stack sx={{ gap: 2 }}>
                  <Typography variant="subtitle1">On Click</Typography>
                  <Box sx={{ width: 222 }}>
                    <Tooltip
                      open={open}
                      placement="top-end"
                      title={
                        <AvatarGroup max={10}>
                          <Avatar alt="Jone Doe" src={`${avatarImage}/avatar-6.png`} />
                          <Avatar alt="Lein Ket" src={`${avatarImage}/avatar-7.png`} />
                          <Avatar alt="Stebin Ben" src={`${avatarImage}/avatar-8.png`} />
                          <Avatar alt="Wungh Tend" src={`${avatarImage}/avatar-9.png`} />
                          <Avatar alt="Trevor Das" src={`${avatarImage}/avatar-10.png`} />
                        </AvatarGroup>
                      }
                    >
                      <AvatarGroup
                        max={6}
                        sx={{ '& .MuiAvatarGroup-avatar': { bgcolor: 'primary.main', cursor: 'pointer' } }}
                        slotProps={{
                          surplus: {
                            onClick: () => {
                              setOpen(!open);
                            }
                          }
                        }}
                      >
                        <Avatar alt="Remy Sharp" src={`${avatarImage}/avatar-1.png`} />
                        <Avatar alt="Travis Howard" src={`${avatarImage}/avatar-2.png`} />
                        <Avatar alt="Cindy Baker" src={`${avatarImage}/avatar-3.png`} />
                        <Avatar alt="Agnes Walker" src={`${avatarImage}/avatar-4.png`} />
                        <Avatar alt="Trevor Henderson" src={`${avatarImage}/avatar-5.png`} />
                        <Avatar alt="Jone Doe" src={`${avatarImage}/avatar-6.png`} />
                        <Avatar alt="Lein Ket" src={`${avatarImage}/avatar-7.png`} />
                        <Avatar alt="Stebin Ben" src={`${avatarImage}/avatar-8.png`} />
                        <Avatar alt="Wungh Tend" src={`${avatarImage}/avatar-9.png`} />
                        <Avatar alt="Trevor Das" src={`${avatarImage}/avatar-10.png`} />
                      </AvatarGroup>
                    </Tooltip>
                  </Box>
                </Stack>
              </MainCard>
              <MainCard title="Sizes" codeString={sizesAvatarCodeString}>
                <Grid container spacing={1} sx={{ alignItems: 'center' }}>
                  <Grid>
                    <Avatar size="xs" alt="Avatar 1" src={`${avatarImage}/avatar-1.png`} />
                  </Grid>
                  <Grid>
                    <Avatar size="sm" alt="Avatar 2" src={`${avatarImage}/avatar-2.png`} />
                  </Grid>
                  <Grid>
                    <Avatar size="md" alt="Avatar 3" src={`${avatarImage}/avatar-3.png`} />
                  </Grid>
                  <Grid>
                    <Avatar size="lg" alt="Avatar 4" src={`${avatarImage}/avatar-4.png`} />
                  </Grid>
                  <Grid>
                    <Avatar size="xl" alt="Avatar 5" src={`${avatarImage}/avatar-5.png`} />
                  </Grid>
                </Grid>
              </MainCard>
              <MainCard title="Fallbacks" codeString={fallbacksAvatarCodeString}>
                <Grid container spacing={1}>
                  <Grid>
                    <Avatar alt="Remy Sharp" src="/broken-image.jpg" color="error" type="filled">
                      B
                    </Avatar>
                  </Grid>
                  <Grid>
                    <Avatar alt="Remy Sharp" src="/broken-image.jpg" color="error" type="outlined" />
                  </Grid>
                  <Grid>
                    <Avatar src="/broken-image.jpg" color="error" />
                  </Grid>
                </Grid>
              </MainCard>
            </Stack>
          </Grid>
        </Grid>
      </ComponentWrapper>
    </>
  );
}
