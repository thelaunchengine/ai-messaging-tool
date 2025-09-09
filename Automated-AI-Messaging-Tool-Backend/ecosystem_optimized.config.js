module.exports = {
  apps: [
    {
      name: 'fastapi-backend',
      script: 'main.py',
      interpreter: 'python3',
      interpreter_args: '-m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4',
      env: {
        NODE_ENV: 'production',
        GEMINI_API_KEY: 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I',
        MAX_BATCH_SIZE: '15',
        MAX_CONCURRENT_WEBSITES: '10',
        TIMEOUT_PER_WEBSITE: '300'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/fastapi-error.log',
      out_file: './logs/fastapi-out.log',
      log_file: './logs/fastapi-combined.log',
      time: true
    },
    {
      name: 'celery-worker-1',
      script: 'celery_worker.py',
      interpreter: 'python3',
      interpreter_args: '--concurrency=8 --queues=scraping,file_processing,ai_processing',
      env: {
        MAX_BATCH_SIZE: '15',
        MAX_CONCURRENT_WEBSITES: '10',
        TIMEOUT_PER_WEBSITE: '300'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/celery-worker-1-error.log',
      out_file: './logs/celery-worker-1-out.log',
      log_file: './logs/celery-worker-1-combined.log',
      time: true
    },
    {
      name: 'celery-worker-2',
      script: 'celery_worker.py',
      interpreter: 'python3',
      interpreter_args: '--concurrency=8 --queues=scraping,file_processing,ai_processing',
      env: {
        MAX_BATCH_SIZE: '15',
        MAX_CONCURRENT_WEBSITES: '10',
        TIMEOUT_PER_WEBSITE: '300'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/celery-worker-2-error.log',
      out_file: './logs/celery-worker-2-out.log',
      log_file: './logs/celery-worker-2-combined.log',
      time: true
    },
    {
      name: 'celery-worker-3',
      script: 'celery_worker.py',
      interpreter: 'python3',
      interpreter_args: '--concurrency=8 --queues=scraping,file_processing,ai_processing',
      env: {
        MAX_BATCH_SIZE: '15',
        MAX_CONCURRENT_WEBSITES: '10',
        TIMEOUT_PER_WEBSITE: '300'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/celery-worker-3-error.log',
      out_file: './logs/celery-worker-3-out.log',
      log_file: './logs/celery-worker-3-combined.log',
      time: true
    },
    {
      name: 'celery-worker-4',
      script: 'celery_worker.py',
      interpreter: 'python3',
      interpreter_args: '--concurrency=8 --queues=scraping,file_processing,ai_processing',
      env: {
        MAX_BATCH_SIZE: '15',
        MAX_CONCURRENT_WEBSITES: '10',
        TIMEOUT_PER_WEBSITE: '300'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/celery-worker-4-error.log',
      out_file: './logs/celery-worker-4-out.log',
      log_file: './logs/celery-worker-4-combined.log',
      time: true
    },
    {
      name: 'celery-monitor',
      script: 'monitor_celery.py',
      interpreter: 'python3',
      env: {
        NODE_ENV: 'production'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      error_file: './logs/celery-monitor-error.log',
      out_file: './logs/celery-monitor-out.log',
      log_file: './logs/celery-monitor-combined.log',
      time: true
    },
    {
      name: 'resource-monitor',
      script: 'monitor_processing.py',
      interpreter: 'python3',
      env: {
        NODE_ENV: 'production'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      error_file: './logs/resource-monitor-error.log',
      out_file: './logs/resource-monitor-out.log',
      log_file: './logs/resource-monitor-combined.log',
      time: true
    },
    {
      name: 'progress-tracker',
      script: 'progress_tracker.py',
      interpreter: 'python3',
      env: {
        NODE_ENV: 'production'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      error_file: './logs/progress-tracker-error.log',
      out_file: './logs/progress-tracker-out.log',
      log_file: './logs/progress-tracker-combined.log',
      time: true
    }
  ]
};
