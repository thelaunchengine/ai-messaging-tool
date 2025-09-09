#!/bin/bash

# File Watcher for Automatic Backend Uploads
# Watches for file changes and automatically uploads to server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Load configuration
if [ -f "upload-config.sh" ]; then
    source upload-config.sh
else
    echo -e "${RED}❌ Configuration file not found. Run setup-ssh-keys.sh first.${NC}"
    exit 1
fi

# Configuration
WATCH_DIRS=("." "celery_tasks" "database" "ai" "scraping")
EXCLUDE_PATTERNS=("*.log" "*.tmp" "*.swp" "*.pyc" "__pycache__" ".git" "venv" "node_modules" ".next" ".env.local" "toUpload" "uploadBackups")
DEBOUNCE_DELAY=5  # seconds
MAX_UPLOAD_FREQUENCY=30  # minimum seconds between uploads

# State variables
LAST_UPLOAD_TIME=0
CHANGED_FILES=()
UPLOAD_PENDING=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Function to check if file should be watched
should_watch_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Skip excluded patterns
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$file" == *"$pattern"* ]]; then
            return 1
        fi
    done
    
    # Check file patterns
    case "$filename" in
        *.py|*.txt|*.yml|*.yaml|*.json|*.sh|*.md|*.env*|requirements*.txt|Dockerfile*|*.config|*.conf)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to add file to changed list
add_changed_file() {
    local file="$1"
    
    # Check if file should be watched
    if should_watch_file "$file"; then
        # Check if file is not already in the list
        if [[ ! " ${CHANGED_FILES[@]} " =~ " ${file} " ]]; then
            CHANGED_FILES+=("$file")
            print_info "File changed: $file"
        fi
    fi
}

# Function to trigger upload
trigger_upload() {
    local current_time=$(date +%s)
    local time_since_last=$((current_time - LAST_UPLOAD_TIME))
    
    # Check if enough time has passed since last upload
    if [ $time_since_last -lt $MAX_UPLOAD_FREQUENCY ]; then
        print_warning "Upload throttled. Waiting ${MAX_UPLOAD_FREQUENCY}s between uploads..."
        return
    fi
    
    if [ ${#CHANGED_FILES[@]} -gt 0 ]; then
        print_status "Triggering upload for ${#CHANGED_FILES[@]} changed files..."
        
        # Create staging directory
        local staging_dir="toUpload/$(date '+%Y%m%d_%H%M%S')"
        mkdir -p "$staging_dir"
        
        # Copy changed files to staging
        for file in "${CHANGED_FILES[@]}"; do
            if [ -f "$file" ]; then
                local dir=$(dirname "$file")
                mkdir -p "$staging_dir/$dir"
                cp "$file" "$staging_dir/$file"
                print_success "Staged: $file"
            fi
        done
        
        # Run upload script
        if ./upload-to-server.sh --staging-dir "$staging_dir" --no-backup; then
            print_success "Automatic upload completed"
            LAST_UPLOAD_TIME=$current_time
        else
            print_error "Automatic upload failed"
        fi
        
        # Clean up staging directory
        rm -rf "$staging_dir"
        
        # Clear changed files list
        CHANGED_FILES=()
        UPLOAD_PENDING=false
    fi
}

# Function to start file watcher
start_watcher() {
    print_status "Starting file watcher..."
    print_info "Watching directories: ${WATCH_DIRS[*]}"
    print_info "Excluding patterns: ${EXCLUDE_PATTERNS[*]}"
    print_info "Debounce delay: ${DEBOUNCE_DELAY}s"
    print_info "Max upload frequency: ${MAX_UPLOAD_FREQUENCY}s"
    echo ""
    
    # Check if fswatch is available
    if command -v fswatch >/dev/null 2>&1; then
        print_info "Using fswatch for file watching"
        watch_with_fswatch
    elif command -v inotifywait >/dev/null 2>&1; then
        print_info "Using inotifywait for file watching"
        watch_with_inotify
    else
        print_error "No file watcher available. Install fswatch or inotify-tools."
        print_info "Install fswatch: brew install fswatch (macOS) or apt-get install inotify-tools (Linux)"
        exit 1
    fi
}

# Function to watch with fswatch
watch_with_fswatch() {
    local watch_args=()
    for dir in "${WATCH_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            watch_args+=("$dir")
        fi
    done
    
    fswatch -o "${watch_args[@]}" | while read -r; do
        # Get list of changed files
        local changed_files_output=$(fswatch -r "${watch_args[@]}" 2>/dev/null | head -n 10)
        
        for file in $changed_files_output; do
            if [ -f "$file" ]; then
                add_changed_file "$file"
            fi
        done
        
        # Set upload pending flag
        UPLOAD_PENDING=true
        
        # Debounce upload
        if [ "$UPLOAD_PENDING" = "true" ]; then
            sleep $DEBOUNCE_DELAY
            trigger_upload
        fi
    done
}

# Function to watch with inotifywait
watch_with_inotify() {
    local watch_args=()
    for dir in "${WATCH_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            watch_args+=("$dir")
        fi
    done
    
    inotifywait -m -r -e modify,create,delete,move "${watch_args[@]}" --format '%w%f %e' | while read -r file event; do
        if [ -f "$file" ]; then
            add_changed_file "$file"
        fi
        
        # Set upload pending flag
        UPLOAD_PENDING=true
        
        # Debounce upload
        if [ "$UPLOAD_PENDING" = "true" ]; then
            sleep $DEBOUNCE_DELAY
            trigger_upload
        fi
    done
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --watch-dirs DIR1,DIR2  Comma-separated list of directories to watch"
    echo "  --exclude PATTERN1,PATTERN2  Comma-separated list of patterns to exclude"
    echo "  --debounce SECONDS      Debounce delay in seconds (default: 5)"
    echo "  --max-frequency SECONDS Maximum upload frequency in seconds (default: 30)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Watch current directory"
    echo "  $0 --watch-dirs src,tests            # Watch specific directories"
    echo "  $0 --debounce 10 --max-frequency 60  # Custom timing"
    echo ""
    echo "File watcher will automatically upload changed files to the server."
    echo "Press Ctrl+C to stop watching."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --watch-dirs)
            IFS=',' read -ra WATCH_DIRS <<< "$2"
            shift 2
            ;;
        --exclude)
            IFS=',' read -ra EXCLUDE_PATTERNS <<< "$2"
            shift 2
            ;;
        --debounce)
            DEBOUNCE_DELAY="$2"
            shift 2
            ;;
        --max-frequency)
            MAX_UPLOAD_FREQUENCY="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if upload script exists
if [ ! -f "upload-to-server.sh" ]; then
    print_error "upload-to-server.sh not found. Run setup-ssh-keys.sh first."
    exit 1
fi

# Check SSH connection
print_status "Testing SSH connection..."
if ! ssh -o ConnectTimeout=10 "$SSH_HOST_ALIAS" "echo 'SSH connection successful'" > /dev/null 2>&1; then
    print_error "SSH connection failed. Run setup-ssh-keys.sh first."
    exit 1
fi
print_success "SSH connection established"

# Start file watcher
echo -e "${PURPLE}👀 File Watcher Started${NC}"
echo "========================"
print_info "Press Ctrl+C to stop watching"
echo ""

# Set up signal handler for graceful shutdown
trap 'echo ""; print_info "Stopping file watcher..."; exit 0' INT TERM

# Start the watcher
start_watcher 