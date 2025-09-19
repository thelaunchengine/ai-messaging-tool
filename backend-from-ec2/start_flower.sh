#!/bin/bash

# Start Flower monitoring for Celery workers
# This script starts Flower on port 5556 to monitor our Celery workers

cd /home/xb3353/Automated-AI-Messaging-Tool-Backend

# Activate virtual environment
source venv/bin/activate

# Start Flower monitoring
# Using the same broker URL as our Celery workers
celery -A celery_app flower --port=5556 --broker=redis://localhost:6379/0 --address=0.0.0.0 