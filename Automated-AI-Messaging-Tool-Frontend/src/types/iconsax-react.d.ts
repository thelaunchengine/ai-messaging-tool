declare module '@wandersonalwes/iconsax-react' {
  import { FC, SVGProps } from 'react';

  interface IconProps extends SVGProps<SVGSVGElement> {
    size?: number;
    color?: string;
    variant?: 'Linear' | 'Outline' | 'Bold' | 'Bulk' | 'TwoTone';
  }

  export const Search: FC<IconProps>;
  export const Document: FC<IconProps>;
  export const MessageQuestion: FC<IconProps>;
  export const Setting2: FC<IconProps>;
  export const Chart2: FC<IconProps>;
  export const DocumentDownload: FC<IconProps>;
  export const Calendar: FC<IconProps>;
  export const Refresh: FC<IconProps>;
  export const Eye: FC<IconProps>;
  export const Menu: FC<IconProps>;
  export const Dashboard: FC<IconProps>;
  export const Upload: FC<IconProps>;
  export const Message: FC<IconProps>;
  export const Settings: FC<IconProps>;
  export const Analytics: FC<IconProps>;
  export const Help: FC<IconProps>;
  export const Logout: FC<IconProps>;
}
