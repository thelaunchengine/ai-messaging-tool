'use client';

import { forwardRef } from 'react';
import Button, { ButtonProps } from '@mui/material/Button';
import { motion } from 'framer-motion';

// ==============================|| ANIMATION BUTTON ||============================== //

const AnimateButton = forwardRef<HTMLButtonElement, ButtonProps>(function AnimateButton({ children, ...props }, ref) {
  return (
    <Button ref={ref} component={motion.button} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} {...props}>
      {children}
    </Button>
  );
});

export default AnimateButton;
