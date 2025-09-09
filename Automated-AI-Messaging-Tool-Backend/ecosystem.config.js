module.exports = {
  apps: [
    {
      name: 'fastapi-backend',
      script: 'venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8001',
      cwd: '/home/xb3353/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      exec_mode: 'fork',           // ADD THIS - Use fork mode for Python
  	interpreter: 'none',         // ADD THIS - No interpreter override
  	restart_delay: 5000,         // ADD THIS - 5 second delay between restarts
  	max_restarts: 10,            // ADD THIS - Max 10 restarts
  	min_uptime: '10s',           // ADD THIS - Must stay up for 10 seconds
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/fastapi-error.log',
      out_file: './logs/fastapi-out.log',
      log_file: './logs/fastapi-combined.log',
      time: true
    },
    {
      name: 'celery-worker-1',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker1@%h --max-tasks-per-child=1000',
      cwd: '/home/xb3353/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/celery-worker-1-error.log',
      out_file: './logs/celery-worker-1-out.log',
      log_file: './logs/celery-worker-1-combined.log',
      time: true,
      restart_delay: 5000,
      interpreter: 'none',
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'celery-worker-2',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker2@%h --max-tasks-per-child=1000',
      cwd: '/home/xb3353/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/celery-worker-2-error.log',
      out_file: './logs/celery-worker-2-out.log',
      log_file: './logs/celery-worker-2-combined.log',
      time: true,
      restart_delay: 5000,
      exec_mode: 'fork',
      interpreter: 'none',
      max_restarts: 10,
      min_uptime: '10s'
    },
  ],
  
  deploy: {
    production: {
      user: 'xb3353',
      host: '103.215.159.51',
      ref: 'origin/main',
      repo: 'https://github.com/xbytedev/Automated-AI-Messaging-Tool-Backend.git',
      path: '/home/xb3353/Automated-AI-Messaging-Tool-Backend',
      'pre-deploy-local': '',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env production',
      'pre-setup': ''
    }
  }
}; 
