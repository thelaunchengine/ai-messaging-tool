#!/bin/bash

# Start Celery Worker 2 Script
cd /home/xb3353/Automated-AI-Messaging-Tool-Backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info --concurrency=1 --queues=default,scraping,file_processing,ai_processing --hostname=worker2@%h --max-tasks-per-child=1000 