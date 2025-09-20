module.exports = {
  apps: [
    {
      name: 'fastapi-backend',
      script: 'venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8001 --workers 6', // Increased workers
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G', // Increased memory
      exec_mode: 'fork',
      interpreter: 'none',
      restart_delay: 3000,
      max_restarts: 15,
      min_uptime: '5s',
      env: {
        PYTHONUNBUFFERED: '1',
        PORT: 8001,
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379',
        CORS_ORIGINS: '["http://34.195.237.115:3000", "http://localhost:3000", "http://localhost:3001"]',
        TIMEOUT_PER_WEBSITE: '30',
        TIMEOUT_PER_BATCH: '300',
        TIMEOUT_PER_CHUNK: '600',
        QUEUE_TIMEOUT: '1800',
        DB_POOL_TIMEOUT: '30'
      },
      error_file: './logs/fastapi-error.log',
      out_file: './logs/fastapi-out.log',
      log_file: './logs/fastapi-combined.log',
      time: true
    },
    {
      name: 'celery-scraper-1',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=6 --queues=scraping,file_processing --hostname=scraper1@%h --max-tasks-per-child=200',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379'
      },
      error_file: './logs/celery-scraper-1-error.log',
      out_file: './logs/celery-scraper-1-out.log',
      log_file: './logs/celery-scraper-1-combined.log',
      time: true,
      restart_delay: 3000,
      max_restarts: 15,
      min_uptime: '5s'
    },
    {
      name: 'celery-scraper-2',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=6 --queues=scraping,file_processing --hostname=scraper2@%h --max-tasks-per-child=200',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379'
      },
      error_file: './logs/celery-scraper-2-error.log',
      out_file: './logs/celery-scraper-2-out.log',
      log_file: './logs/celery-scraper-2-combined.log',
      time: true,
      restart_delay: 3000,
      max_restarts: 15,
      min_uptime: '5s'
    },
    {
      name: 'celery-ai-1',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=4 --queues=ai_processing --hostname=ai1@%h --max-tasks-per-child=300',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '3G',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379'
      },
      error_file: './logs/celery-ai-1-error.log',
      out_file: './logs/celery-ai-1-out.log',
      log_file: './logs/celery-ai-1-combined.log',
      time: true,
      restart_delay: 3000,
      max_restarts: 15,
      min_uptime: '5s'
    },
    {
      name: 'celery-ai-2',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=4 --queues=ai_processing --hostname=ai2@%h --max-tasks-per-child=300',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '3G',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379'
      },
      error_file: './logs/celery-ai-2-error.log',
      out_file: './logs/celery-ai-2-out.log',
      log_file: './logs/celery-ai-2-combined.log',
      time: true,
      restart_delay: 3000,
      max_restarts: 15,
      min_uptime: '5s'
    },
    // ULTRA-FAST FORM SUBMISSION WORKERS
    {
      name: 'celery-forms-1',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=20 --queues=form_submission --hostname=forms1@%h --max-tasks-per-child=500',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '4G', // High memory for parallel processing
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379'
      },
      error_file: './logs/celery-forms-1-error.log',
      out_file: './logs/celery-forms-1-out.log',
      log_file: './logs/celery-forms-1-combined.log',
      time: true,
      restart_delay: 2000,
      max_restarts: 20,
      min_uptime: '3s'
    },
    {
      name: 'celery-forms-2',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=20 --queues=form_submission --hostname=forms2@%h --max-tasks-per-child=500',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '4G',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379'
      },
      error_file: './logs/celery-forms-2-error.log',
      out_file: './logs/celery-forms-2-out.log',
      log_file: './logs/celery-forms-2-combined.log',
      time: true,
      restart_delay: 2000,
      max_restarts: 20,
      min_uptime: '3s'
    },
    {
      name: 'celery-forms-3',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=20 --queues=form_submission --hostname=forms3@%h --max-tasks-per-child=500',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '4G',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379'
      },
      error_file: './logs/celery-forms-3-error.log',
      out_file: './logs/celery-forms-3-out.log',
      log_file: './logs/celery-forms-3-combined.log',
      time: true,
      restart_delay: 2000,
      max_restarts: 20,
      min_uptime: '3s'
    },
    {
      name: 'celery-priority',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=4 --queues=priority --hostname=priority@%h --max-tasks-per-child=1000',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379'
      },
      error_file: './logs/celery-priority-error.log',
      out_file: './logs/celery-priority-out.log',
      log_file: './logs/celery-priority-combined.log',
      time: true,
      restart_delay: 3000,
      max_restarts: 15,
      min_uptime: '5s'
    }
  ]
};
