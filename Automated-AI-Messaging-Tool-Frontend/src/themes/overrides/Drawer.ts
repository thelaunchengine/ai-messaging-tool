// ==============================|| OVERRIDES - DRAWER ||============================== //

export default function Drawer() {
  return {
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#F9FAFB', // Very light gray/white background
          backgroundImage: 'none',
          boxShadow: 'none' // No shadow
        }
      }
    }
  };
}
