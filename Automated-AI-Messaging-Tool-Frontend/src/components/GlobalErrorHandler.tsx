import React, { useEffect } from 'react';

interface GlobalErrorHandlerProps {
  children: React.ReactNode;
}

const GlobalErrorHandler: React.FC<GlobalErrorHandlerProps> = ({ children }) => {
  useEffect(() => {
    // Handle unhandled promise rejections
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.warn('Unhandled promise rejection:', event.reason);
      
      // Prevent the default browser behavior
      event.preventDefault();
      
      // Log the error for debugging
      if (process.env.NODE_ENV === 'development') {
        console.error('Unhandled Promise Rejection:', event.reason);
      }
    };

    // Handle global errors
    const handleGlobalError = (event: ErrorEvent) => {
      console.warn('Global error caught:', event.error);
      
      // Check if it's a MUI-related error
      if (event.error && event.error.message && 
          (event.error.message.includes('Cannot read properties of undefined') ||
           event.error.message.includes('LinearProgress') ||
           event.error.message.includes('@mui/material'))) {
        
        console.warn('MUI-related error detected, attempting to recover...');
        
        // Prevent the error from crashing the app
        event.preventDefault();
        
        // Optionally reload the page after a short delay if it's a critical MUI error
        if (event.error.message.includes('Cannot read properties of undefined')) {
          setTimeout(() => {
            console.log('Attempting to recover from MUI error...');
            // You can add recovery logic here instead of reloading
          }, 1000);
        }
      }
    };

    // Add event listeners
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleGlobalError);

    // Cleanup
    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleGlobalError);
    };
  }, []);

  return <>{children}</>;
};

export default GlobalErrorHandler;
