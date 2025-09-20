#!/bin/bash

# Start Celery Worker Script
cd /var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info --concurrency=1 --queues=default,scraping,file_processing,ai_processing --hostname=worker4@%h --max-tasks-per-child=1000
