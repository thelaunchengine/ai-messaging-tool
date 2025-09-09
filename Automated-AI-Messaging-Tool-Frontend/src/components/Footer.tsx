import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Footer() {
  const pathname = usePathname();
  const isAdminPage = pathname?.startsWith('/admin');

  return (
    <Box
      component="footer"
      sx={{
        width: '100%',
        bgcolor: 'background.paper',
        borderTop: '1px solid',
        borderColor: 'divider',
        py: 2,
        px: { xs: 2, md: 4 },
        mt: 'auto',
        textAlign: 'center'
      }}
    >
      {!isAdminPage && (
        <Stack direction="row" spacing={3} justifyContent="center" alignItems="center" mb={1}>
          <Link href="/about" passHref legacyBehavior>
            <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
              About
            </Typography>
          </Link>
        </Stack>
      )}
      <Typography variant="caption" color="text.secondary">
        © {new Date().getFullYear()} AI Messaging Tool.
      </Typography>
    </Box>
  );
}
