#!/bin/bash

# Start AI Messaging Backend with Celery - Local Development
echo "🚀 Starting AI Messaging Backend with Celery..."

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

echo "✅ Redis is running"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start FastAPI server in background
echo "🌐 Starting FastAPI server on http://localhost:8000..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > logs/fastapi.log 2>&1 &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 3

# Start Celery worker in background
echo "🔧 Starting Celery worker..."
celery -A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker@%h --max-tasks-per-child=1000 > logs/celery.log 2>&1 &
CELERY_PID=$!

echo ""
echo "🎉 AI Messaging Backend is running!"
echo ""
echo "📊 Services:"
echo "  🌐 FastAPI Server: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo "  🔧 Celery Worker: Running with 2 processes"
echo "  🔗 Redis: Running on localhost:6379"
echo ""
echo "📋 Logs:"
echo "  FastAPI: logs/fastapi.log"
echo "  Celery: logs/celery.log"
echo ""
echo "🛑 To stop all services, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $FASTAPI_PID 2>/dev/null
    kill $CELERY_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait 