/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true,
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'flagcdn.com',
        pathname: '**'
      }
    ]
  },
  // Disable Next.js error overlay and static indicator toasts
  devIndicators: {
    buildActivity: false,
    buildActivityPosition: 'bottom-right',
  },
  // Disable error overlay
  onDemandEntries: {
    // period (in ms) where the server will keep pages in the buffer
    maxInactiveAge: 25 * 1000,
    // number of pages that should be kept simultaneously without being disposed
    pagesBufferLength: 2,
  },
  // Add modularize imports for MUI optimization
  modularizeImports: {
    '@mui/material': {
      transform: '@mui/material/{{member}}'
    },
    '@mui/lab': {
      transform: '@mui/lab/{{member}}'
    }
  },
  webpack: (config, { isServer }) => {
    // Handle SVG files
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });

    // Better MUI compatibility
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    // Handle MUI theme issues
    config.module.rules.push({
      test: /\.m?js$/,
      resolve: {
        fullySpecified: false,
      },
    });

    return config;
  },
  transpilePackages: [
    '@mui/material', 
    '@mui/system', 
    '@mui/icons-material',
    '@emotion/react',
    '@emotion/styled'
  ],
  // Add experimental features for better error handling
  experimental: {
    // Optimize package imports
    optimizePackageImports: ['@mui/material', '@mui/icons-material'],
  },
  // Add environment variables
  env: {
    NEXT_APP_VERSION: 'v3.0.0',
    NEXTAUTH_SECRET: 'LlKq6ZtYbr+hTC073mAmAh9/h2HwMfsFo4hrfCx5mLg=',
    NEXT_APP_GOOGLE_MAPS_API_KEY: 'AIzaSyAXv4RQK39CskcIB8fvM1Q7XCofZcLxUXw',
    NEXT_APP_MAPBOX_ACCESS_TOKEN: 'pk.eyJ1IjoicmFrc2VzaC1uYWtyYW5pIiwiYSI6ImNsbDYzZGZtMjBob3AzZW96YXYxeHR5c3oifQ.ps6azYbr7M3rGk_QTguMEQ',
    NEXT_APP_API_URL: 'https://mock-data-api-nextjs.vercel.app',
    NEXT_APP_JWT_SECRET: 'ikRgjkhi15HJiU78-OLKfjngiu',
    NEXT_APP_JWT_TIMEOUT: '86400',
    NEXTAUTH_SECRET_KEY: 'LlKq6ZtYbr+hTC073mAmAh9/h2HwMfsFo4hrfCx5mLg=',
    PYTHON_API_URL: 'http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001',
    NEXT_PUBLIC_PYTHON_BACKEND_URL: 'http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001'
  }
}

module.exports = nextConfig 