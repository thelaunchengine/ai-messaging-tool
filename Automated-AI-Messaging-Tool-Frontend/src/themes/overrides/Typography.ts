// ==============================|| OVERRIDES - TYPOGRAPHY ||============================== //

export default function Typography() {
  return {
    MuiTypography: {
      styleOverrides: {
        root: {
          fontSize: '16px', // Base font size
          fontFamily: '"Poppins", "Inter", "Roboto", "Helvetica Neue", Arial, sans-serif',
          color: '#0f172a' // Main text color
        },
        h1: {
          fontSize: '2.5rem',
          fontWeight: 700,
          lineHeight: 1.2,
          color: '#0f172a' // Main text color
        },
        h2: {
          fontSize: '2rem',
          fontWeight: 700,
          lineHeight: 1.3,
          color: '#0f172a' // Main text color
        },
        h3: {
          fontSize: '1.75rem',
          fontWeight: 600,
          lineHeight: 1.3,
          color: '#0f172a' // Main text color
        },
        h4: {
          fontSize: '1.5rem',
          fontWeight: 600,
          lineHeight: 1.4,
          color: '#0f172a' // Main text color
        },
        h5: {
          fontSize: '1.25rem',
          fontWeight: 600,
          lineHeight: 1.4,
          color: '#0f172a' // Main text color
        },
        h6: {
          fontSize: '1.125rem',
          fontWeight: 600,
          lineHeight: 1.4,
          color: '#0f172a' // Main text color
        },
        subtitle1: {
          fontSize: '1rem',
          fontWeight: 500,
          lineHeight: 1.5,
          color: '#9095a4' // Paragraph color
        },
        subtitle2: {
          fontSize: '0.875rem',
          fontWeight: 500,
          lineHeight: 1.5,
          color: '#9095a4' // Paragraph color
        },
        body1: {
          fontSize: '1rem',
          fontWeight: 400,
          lineHeight: 1.6,
          color: '#9095a4' // Paragraph color
        },
        body2: {
          fontSize: '0.875rem',
          fontWeight: 400,
          lineHeight: 1.6,
          color: '#9095a4' // Paragraph color
        },
        caption: {
          fontSize: '0.75rem',
          fontWeight: 400,
          lineHeight: 1.5,
          color: '#71767b' // Icons color
        },
        gutterBottom: {
          marginBottom: 16
        }
      }
    }
  };
}
