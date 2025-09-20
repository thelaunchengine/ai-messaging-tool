module.exports = {
  apps: [
    {
      name: 'frontend',
      script: 'npm',
      args: 'start',
      cwd: '/home/ubuntu/ai-messaging-tool/Automated-AI-Messaging-Tool-Frontend',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXTAUTH_URL: 'http://34.195.237.115:3000',
        NEXTAUTH_SECRET: 'your-secret-key-here',
        PYTHON_API_URL: 'http://98.85.16.204:8001',
        NEXT_PUBLIC_PYTHON_BACKEND_URL: 'http://98.85.16.204:8001'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true
    }
  ]
};
