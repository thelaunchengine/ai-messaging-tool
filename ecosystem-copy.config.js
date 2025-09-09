module.exports = {
  apps: [
    {
      name: 'Frontend-Copy',
      script: 'npm',
      args: 'run dev',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      cwd: '/home/xb3353/aimsg-copy-frontend',
      env: {
        NODE_ENV: 'development',
        PORT: 3002,
        NEXT_PUBLIC_BACKEND_URL: 'http://103.215.159.51:8002',
        NEXTAUTH_URL: 'http://103.215.159.51:3002',
        NEXTAUTH_SECRET: 'your-nextauth-secret-key-here',
        NEXT_PUBLIC_BASE_URL: 'http://103.215.159.51:3002'
      }
    },
    {
      name: 'Backend-Copy',
      script: '/home/xb3353/aimsg-copy-backend/venv/bin/python',
      args: 'main.py',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      cwd: '/home/xb3353/aimsg-copy-backend',
      env: {
        PORT: 8002,
        HOST: '0.0.0.0'
      }
    }
  ]
};
