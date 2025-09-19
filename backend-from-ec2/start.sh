#!/bin/bash
echo "Starting with Python version:"
python --version

echo "Starting Celery worker in background..."
celery -A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker1@%h --max-tasks-per-child=1000 &

echo "Starting FastAPI app..."
uvicorn main:app --host 0.0.0.0 --port $PORT 