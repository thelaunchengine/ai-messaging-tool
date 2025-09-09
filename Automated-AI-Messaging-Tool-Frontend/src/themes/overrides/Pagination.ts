// ==============================|| OVERRIDES - PAGINATION ||============================== //

export default function Pagination() {
  return {
    MuiPagination: {
      defaultProps: {
        shape: 'rounded'
      },
      styleOverrides: { 
        ul: { 
          rowGap: 8,
          columnGap: 4
        },
        root: {
          '& .MuiPaginationItem-root': {
            borderRadius: '8px',
            margin: '0 2px',
            minWidth: '40px',
            height: '40px',
            fontSize: '0.875rem',
            fontWeight: 500,
            transition: 'all 0.2s ease',
            '&:hover': {
              backgroundColor: '#F3F4F6',
              transform: 'translateY(-1px)'
            },
            '&.Mui-selected': {
              backgroundColor: '#7B3FF2',
              color: '#FFFFFF',
              '&:hover': {
                backgroundColor: '#6B21A8'
              }
            }
          }
        }
      }
    }
  };
}
