module.exports = {
  apps: [
    {
      name: 'aimsg-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/home/xb3353/Automated-AI-Messaging-Tool-Frontend',
      env: {
        NODE_ENV: 'development',
        PORT: 3001,
        NEXTAUTH_URL: 'http://103.215.159.51:3001',
        NEXTAUTH_SECRET: 'your-secret-key-here',
        PYTHON_API_URL: 'http://103.215.159.51:8001'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: '/home/xb3353/Automated-AI-Messaging-Tool-Frontend/logs/err.log',
      out_file: '/home/xb3353/Automated-AI-Messaging-Tool-Frontend/logs/out.log',
      log_file: '/home/xb3353/Automated-AI-Messaging-Tool-Frontend/logs/combined.log',
      time: true
    }
  ]
}; 