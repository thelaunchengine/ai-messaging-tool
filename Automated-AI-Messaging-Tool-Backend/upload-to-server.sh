#!/bin/bash

# Backend Upload Script
# Uploads Python backend files to server and restarts the service

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

# Function to check if file should be uploaded
should_upload_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Skip certain files and directories
    case "$filename" in
        .DS_Store|*.log|*.tmp|*.swp|*.pyc|__pycache__|.git|venv|node_modules|.next|.env.local)
            return 1
            ;;
    esac
    
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

# Function to create backup
create_backup() {
    local backup_dir="$UPLOAD_BACKUP_DIR/$(date '+%Y%m%d_%H%M%S')"
    print_status "Creating backup at $backup_dir"
    
    mkdir -p "$backup_dir"
    
    # Create tar archive of current server state
    ssh "$SSH_HOST_ALIAS" "cd $SERVER_PATH && tar -czf /tmp/backend_backup_$(date '+%Y%m%d_%H%M%S').tar.gz ." || {
        print_warning "Failed to create server backup"
    }
    
    print_success "Backup created"
}

# Function to upload files
upload_files() {
    local source_dir="$1"
    local files_to_upload=()
    
    print_status "Scanning for files to upload..."
    
    # Find all files that should be uploaded
    while IFS= read -r -d '' file; do
        if should_upload_file "$file"; then
            files_to_upload+=("$file")
        fi
    done < <(find "$source_dir" -type f -print0 2>/dev/null || true)
    
    if [ ${#files_to_upload[@]} -eq 0 ]; then
        print_warning "No files found to upload"
        return 1
    fi
    
    print_info "Found ${#files_to_upload[@]} files to upload"
    
    # Create temporary directory on server
    local temp_dir=$(ssh "$SSH_HOST_ALIAS" "mktemp -d /tmp/backend_upload_XXXXXX")
    print_status "Created temp directory: $temp_dir"
    
    # Upload files
    local uploaded_count=0
    for file in "${files_to_upload[@]}"; do
        local relative_path="${file#$source_dir/}"
        local remote_path="$temp_dir/$relative_path"
        local remote_dir=$(dirname "$remote_path")
        
        # Create directory structure on server
        ssh "$SSH_HOST_ALIAS" "mkdir -p '$remote_dir'"
        
        # Upload file
        if scp -q "$file" "$SSH_HOST_ALIAS:$remote_path"; then
            print_success "Uploaded: $relative_path"
            ((uploaded_count++))
        else
            print_error "Failed to upload: $relative_path"
        fi
    done
    
    print_success "Uploaded $uploaded_count files"
    
    # Move files from temp to actual location
    print_status "Moving files to final location..."
    ssh "$SSH_HOST_ALIAS" "cd $temp_dir && find . -type f -exec cp --parents {} $SERVER_PATH \;"
    
    # Clean up temp directory
    ssh "$SSH_HOST_ALIAS" "rm -rf $temp_dir"
    
    return 0
}

# Function to restart backend service
restart_backend_service() {
    print_status "Restarting backend services..."
    
    # Restart FastAPI backend service
    if ssh "$SSH_HOST_ALIAS" "sudo systemctl restart ai-messaging-backend.service"; then
        print_success "FastAPI backend service restarted"
    else
        print_warning "Failed to restart FastAPI service"
    fi
    
    # Restart Celery worker service (if it exists)
    if ssh "$SSH_HOST_ALIAS" "sudo systemctl restart ai-messaging-celery.service 2>/dev/null"; then
        print_success "Celery worker service restarted"
    else
        print_info "Celery service not found, restarting manually"
        ssh "$SSH_HOST_ALIAS" "cd $SERVER_PATH && pkill -f 'celery.*worker' && sleep 2 && source venv/bin/activate && celery -A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker@%h --max-tasks-per-child=1000 > logs/celery.log 2>&1 &"
    fi
    
    # Wait a moment for services to start
    sleep 3
    
    # Check if services are running
    if ssh "$SSH_HOST_ALIAS" "curl -s http://localhost:$BACKEND_PORT/health > /dev/null"; then
        print_success "Backend services restarted successfully"
    else
        print_warning "Backend service may not be running. Check manually."
    fi
    
    # Check Celery workers
    if ssh "$SSH_HOST_ALIAS" "ps aux | grep celery | grep -v grep | wc -l" | grep -q "[1-9]"; then
        print_success "Celery workers are running"
    else
        print_warning "Celery workers may not be running"
    fi
}

# Function to clean up staging directory
cleanup_staging() {
    if [ "$CLEANUP_AFTER_UPLOAD" = "true" ] && [ -d "$UPLOAD_STAGING_DIR" ]; then
        print_status "Cleaning up staging directory..."
        rm -rf "$UPLOAD_STAGING_DIR"
        print_success "Staging directory cleaned up"
    fi
}

# Function to show upload summary
show_summary() {
    echo ""
    echo -e "${PURPLE}📊 Upload Summary${NC}"
    echo "=================="
    echo -e "${CYAN}Server:${NC} $SERVER_USER@$SERVER_HOST"
    echo -e "${CYAN}Path:${NC} $SERVER_PATH"
    echo -e "${CYAN}Port:${NC} $BACKEND_PORT"
    echo -e "${CYAN}Service:${NC} $BACKEND_SERVICE_NAME"
    echo ""
    echo -e "${GREEN}🌐 Live URL:${NC} http://$SERVER_HOST:$BACKEND_PORT"
    echo -e "${GREEN}📚 API Docs:${NC} http://$SERVER_HOST:$BACKEND_PORT/docs"
    echo -e "${GREEN}🔍 Health Check:${NC} http://$SERVER_HOST:$BACKEND_PORT/health"
    echo ""
}

# Main execution
main() {
    echo -e "${PURPLE}🚀 Backend Upload Script${NC}"
    echo "========================"
    
    # Check SSH connection
    print_status "Testing SSH connection..."
    if ! ssh -o ConnectTimeout=10 "$SSH_HOST_ALIAS" "echo 'SSH connection successful'" > /dev/null 2>&1; then
        print_error "SSH connection failed. Run setup-ssh-keys.sh first."
        exit 1
    fi
    print_success "SSH connection established"
    
    # Determine source directory
    local source_dir="."
    if [ -d "$UPLOAD_STAGING_DIR" ]; then
        source_dir="$UPLOAD_STAGING_DIR"
        print_info "Using staging directory: $source_dir"
    else
        print_info "Using current directory as source"
    fi
    
    # Create backup
    if [ "$CREATE_BACKUP" = "true" ]; then
        create_backup
    fi
    
    # Upload files
    if upload_files "$source_dir"; then
        print_success "File upload completed"
    else
        print_error "File upload failed"
        exit 1
    fi
    
    # Restart service
    restart_backend_service
    
    # Clean up
    cleanup_staging
    
    # Show summary
    show_summary
    
    print_success "Upload completed successfully!"
}

# Parse command line arguments
CLEANUP_AFTER_UPLOAD="true"
CREATE_BACKUP="true"

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cleanup)
            CLEANUP_AFTER_UPLOAD="false"
            shift
            ;;
        --no-backup)
            CREATE_BACKUP="false"
            shift
            ;;
        --staging-dir)
            UPLOAD_STAGING_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-cleanup     Don't clean up staging directory after upload"
            echo "  --no-backup      Don't create backup before upload"
            echo "  --staging-dir DIR Use custom staging directory"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Upload current directory"
            echo "  $0 --no-cleanup      # Upload without cleanup"
            echo "  $0 --staging-dir src # Upload from src directory"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main "$@" 