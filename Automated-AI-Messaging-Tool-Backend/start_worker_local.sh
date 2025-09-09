#!/bin/bash

# Start Celery Worker for AI Messaging Backend
echo "🚀 Starting Celery Worker..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup_local.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Starting Redis..."
    brew services start redis
    sleep 2
fi

# Start Celery worker
echo "📋 Starting Celery worker with 2 concurrent processes..."
echo "🔗 Queues: default, scraping, file_processing, ai_processing"
echo "📊 Log level: info"
echo ""

celery -A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker@%h --max-tasks-per-child=1000 