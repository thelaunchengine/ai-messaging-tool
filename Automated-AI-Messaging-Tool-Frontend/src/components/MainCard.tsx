'use client';

import { forwardRef } from 'react';
import { Card, CardContent, CardHeader, Divider, Typography } from '@mui/material';

interface MainCardProps {
  border?: boolean;
  boxShadow?: boolean;
  children: React.ReactNode;
  content?: boolean;
  contentClass?: string;
  contentSX?: object;
  darkTitle?: boolean;
  divider?: boolean;
  elevation?: number;
  secondary?: React.ReactNode;
  shadow?: string;
  sx?: object;
  title?: React.ReactNode;
}

const MainCard = forwardRef<HTMLDivElement, MainCardProps>(
  (
    {
      border = true,
      boxShadow,
      children,
      content = true,
      contentClass = '',
      contentSX = {},
      darkTitle,
      divider = true,
      elevation,
      secondary,
      shadow,
      sx = {},
      title,
      ...others
    },
    ref
  ) => {
    return (
      <Card
        elevation={elevation || 0}
        ref={ref}
        {...others}
        sx={{
          border: border ? '1px solid' : 'none',
          borderRadius: '16px',
          borderColor: 'rgba(0, 0, 0, 0.08)',
          boxShadow: boxShadow ? shadow || '0 4px 24px rgba(0, 0, 0, 0.06)' : 'none',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          backgroundColor: '#FFFFFF',
          '&:hover': {
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            transform: 'translateY(-2px)'
          },
          ...sx
        }}
      >
        {/* card header and action */}
        {!darkTitle && title && (
          <CardHeader 
            sx={{ 
              p: 4,
              '& .MuiCardHeader-title': {
                fontSize: '1.25rem',
                fontWeight: 600,
                color: '#1A1A1A'
              }
            }} 
            title={<Typography variant="h5">{title}</Typography>} 
            action={secondary} 
          />
        )}
        {darkTitle && title && (
          <CardHeader 
            sx={{ 
              p: 4,
              '& .MuiCardHeader-title': {
                fontSize: '1.5rem',
                fontWeight: 700,
                color: '#1A1A1A'
              }
            }} 
            title={<Typography variant="h4">{title}</Typography>} 
            action={secondary} 
          />
        )}

        {/* content & header divider */}
        {title && divider && <Divider sx={{ borderColor: 'rgba(0, 0, 0, 0.08)' }} />}

        {/* card content */}
        {content && (
          <CardContent 
            sx={{ 
              p: 4,
              '&:last-child': { pb: 4 },
              ...contentSX 
            }} 
            className={contentClass}
          >
            {children}
          </CardContent>
        )}
        {!content && children}
      </Card>
    );
  }
);

MainCard.displayName = 'MainCard';

export default MainCard;
