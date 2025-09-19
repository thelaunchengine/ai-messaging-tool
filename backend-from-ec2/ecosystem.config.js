module.exports = {
  apps: [
    {
      name: 'fastapi-backend',
      script: 'venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8001',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      exec_mode: 'fork',
      interpreter: 'none',
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s',
      env: {
        NODE_ENV: 'production',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://localhost:6379/0',
        GEMINI_API_KEY: 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I',
        TESTING_MODE_ENABLED: 'false',
        MAX_AI_MESSAGES_PER_FILE: '30',
        PYTHON_API_URL: 'http://98.85.16.204:8001'
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
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://localhost:6379/0',
        GEMINI_API_KEY: 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I',
        TESTING_MODE_ENABLED: 'false',
        MAX_AI_MESSAGES_PER_FILE: '30',
        PYTHON_API_URL: 'http://98.85.16.204:8001'
      },
      error_file: './logs/celery-worker-1-error.log',
      out_file: './logs/celery-worker-1-out.log',
      log_file: './logs/celery-worker-1-combined.log',
      time: true,
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'celery-worker-2',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker2@%h --max-tasks-per-child=1000',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://localhost:6379/0',
        GEMINI_API_KEY: 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I',
        TESTING_MODE_ENABLED: 'false',
        MAX_AI_MESSAGES_PER_FILE: '30',
        PYTHON_API_URL: 'http://98.85.16.204:8001'
      },
      error_file: './logs/celery-worker-2-error.log',
      out_file: './logs/celery-worker-2-out.log',
      log_file: './logs/celery-worker-2-combined.log',
      time: true,
      restart_delay: 5000,
      exec_mode: 'fork',
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
