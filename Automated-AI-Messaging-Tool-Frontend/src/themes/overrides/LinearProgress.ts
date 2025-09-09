// ==============================|| OVERRIDES - LINEAR PROGRESS ||============================== //

export default function LinearProgress(theme?: any) {
  try {
    return {
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            height: 6,
            borderRadius: 100,
            backgroundColor: theme?.palette?.grey?.[100] || '#f5f5f5'
          },
          bar: {
            borderRadius: 100,
            backgroundColor: theme?.palette?.primary?.main || '#6200ff'
          }
        }
      }
    };
  } catch (error) {
    console.warn('LinearProgress override error:', error);
    return {
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            height: 6,
            borderRadius: 100,
            backgroundColor: '#f5f5f5'
          },
          bar: {
            borderRadius: 100,
            backgroundColor: '#6200ff'
          }
        }
      }
    };
  }
}
