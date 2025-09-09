declare module 'components/MainCard' {
  import { ReactNode } from 'react';
  import { SxProps, Theme } from '@mui/material';

  interface MainCardProps {
    title?: string;
    children: ReactNode;
    sx?: SxProps<Theme>;
  }

  const MainCard: React.FC<MainCardProps>;
  export default MainCard;
}

declare module 'config' {
  export const GRID_COMMON_SPACING: number;
}
