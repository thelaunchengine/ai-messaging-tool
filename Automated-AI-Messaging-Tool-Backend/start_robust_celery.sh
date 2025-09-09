#!/bin/bash

# Robust Celery Startup Script
# Ensures workers are properly started and monitored

set -e

# Configuration
BACKEND_DIR="/home/xb3353/Automated-AI-Messaging-Tool-Backend"
VENV_PATH="$BACKEND_DIR/venv/bin/activate"
LOG_DIR="$BACKEND_DIR/logs"
MAX_RESTART_ATTEMPTS=5
RESTART_DELAY=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to check if a process is running
is_process_running() {
    local pattern="$1"
    pgrep -f "$pattern" > /dev/null 2>&1
}

# Function to kill processes
kill_processes() {
    local pattern="$1"
    if is_process_running "$pattern"; then
        log "Killing existing processes matching: $pattern"
        pkill -f "$pattern" || true
        sleep 2
    fi
}

# Function to start a single worker
start_worker() {
    local worker_name="$1"
    local worker_num="$2"
    local log_file="$LOG_DIR/celery_${worker_name}.log"
    
    log "Starting $worker_name..."
    
    # Kill existing worker if running
    kill_processes "celery.*$worker_name"
    
    # Start new worker
    cd "$BACKEND_DIR"
    source "$VENV_PATH"
    
    nohup celery -A celery_app worker \
        --loglevel=info \
        --concurrency=2 \
        --queues=default,scraping,file_processing,ai_processing \
        --hostname=${worker_name}@%h \
        --max-tasks-per-child=1000 \
        > "$log_file" 2>&1 &
    
    local worker_pid=$!
    log "$worker_name started with PID: $worker_pid"
    
    # Wait a bit and check if it's still running
    sleep 5
    if ! is_process_running "celery.*$worker_name"; then
        error "$worker_name failed to start properly"
        return 1
    fi
    
    log "$worker_name is running successfully"
    return 0
}

# Function to check worker health
check_worker_health() {
    local worker_name="$1"
    
    # Check if process is running
    if ! is_process_running "celery.*$worker_name"; then
        return 1
    fi
    
    # Check if worker responds to Celery inspect
    cd "$BACKEND_DIR"
    source "$VENV_PATH"
    
    if timeout 10 celery -A celery_app inspect active > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to restart worker with retry logic
restart_worker_with_retry() {
    local worker_name="$1"
    local worker_num="$2"
    local attempts=0
    
    while [ $attempts -lt $MAX_RESTART_ATTEMPTS ]; do
        attempts=$((attempts + 1))
        log "Attempt $attempts to start $worker_name"
        
        if start_worker "$worker_name" "$worker_num"; then
            log "$worker_name started successfully on attempt $attempts"
            return 0
        else
            error "$worker_name failed to start on attempt $attempts"
            if [ $attempts -lt $MAX_RESTART_ATTEMPTS ]; then
                warning "Waiting $RESTART_DELAY seconds before retry..."
                sleep $RESTART_DELAY
            fi
        fi
    done
    
    error "$worker_name failed to start after $MAX_RESTART_ATTEMPTS attempts"
    return 1
}

# Main startup function
start_all_workers() {
    log "Starting robust Celery workers..."
    
    # Kill any existing Celery processes
    kill_processes "celery.*worker"
    
    # Start workers
    local success=true
    
    if ! restart_worker_with_retry "worker1" 1; then
        success=false
    fi
    
    if ! restart_worker_with_retry "worker2" 2; then
        success=false
    fi
    
    if [ "$success" = true ]; then
        log "All workers started successfully"
        
        # Wait a moment and verify all workers are healthy
        sleep 10
        
        local healthy_workers=0
        if check_worker_health "worker1"; then
            healthy_workers=$((healthy_workers + 1))
        fi
        if check_worker_health "worker2"; then
            healthy_workers=$((healthy_workers + 1))
        fi
        
        if [ $healthy_workers -eq 2 ]; then
            log "All workers are healthy and responding"
            return 0
        else
            error "Only $healthy_workers/2 workers are healthy"
            return 1
        fi
    else
        error "Failed to start all workers"
        return 1
    fi
}

# Function to check system dependencies
check_dependencies() {
    log "Checking system dependencies..."
    
    # Check if virtual environment exists
    if [ ! -f "$VENV_PATH" ]; then
        error "Virtual environment not found at $VENV_PATH"
        return 1
    fi
    
    # Check if Redis is running
    if ! redis-cli ping > /dev/null 2>&1; then
        error "Redis is not running"
        return 1
    fi
    
    # Check if PostgreSQL is accessible
    cd "$BACKEND_DIR"
    source "$VENV_PATH"
    if ! python3 -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:cDtrtoOqpdkAzMcLSd%401847@localhost:5432/aimsgdb'); conn.close(); print('DB OK')" > /dev/null 2>&1; then
        error "Database connection failed"
        return 1
    fi
    
    log "All dependencies are available"
    return 0
}

# Main execution
main() {
    log "=== Robust Celery Startup Script ==="
    
    # Check dependencies
    if ! check_dependencies; then
        error "Dependency check failed. Exiting."
        exit 1
    fi
    
    # Start all workers
    if start_all_workers; then
        log "=== Celery workers started successfully ==="
        log "Workers are running and healthy"
        log "Logs are available in: $LOG_DIR"
        exit 0
    else
        error "=== Failed to start Celery workers ==="
        exit 1
    fi
}

# Run main function
main "$@" 