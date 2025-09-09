// ==============================|| OVERRIDES - TABS ||============================== //

export default function Tabs() {
  return {
    MuiTabs: {
      styleOverrides: {
        vertical: {
          overflow: 'visible'
        },
        root: {
          '& .MuiTabs-indicator': {
            backgroundColor: '#7B3FF2', // Purple indicator
            height: '3px', // Thicker indicator
            borderRadius: '2px' // Rounded indicator
          }
        }
      }
    }
  };
}
