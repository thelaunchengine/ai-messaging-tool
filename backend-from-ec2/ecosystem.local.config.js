module.exports = {
  apps: [
    {
      name: 'fastapi-backend',
      script: 'main.py',
      interpreter: 'python3',
      interpreter_args: '-m uvicorn main:app --host 0.0.0.0 --port 8000',
      cwd: '/Users/apple/Downloads/ai-messaging-python-backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PYTHONPATH: '/Users/apple/Downloads/ai-messaging-python-backend'
      },
      error_file: './logs/fastapi-error.log',
      out_file: './logs/fastapi-out.log',
      log_file: './logs/fastapi-combined.log',
      time: true
    },
    {
      name: 'celery-worker-1',
      script: 'celery_app.py',
      interpreter: 'python3',
      interpreter_args: '-A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker1@%h --max-tasks-per-child=1000',
      cwd: '/Users/apple/Downloads/ai-messaging-python-backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        NODE_ENV: 'development',
        PYTHONPATH: '/Users/apple/Downloads/ai-messaging-python-backend'
      },
      error_file: './logs/celery-worker-1-error.log',
      out_file: './logs/celery-worker-1-out.log',
      log_file: './logs/celery-worker-1-combined.log',
      time: true,
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
