#!/bin/bash

# Test Automatic Upload and Service Restart
# This script demonstrates the automatic upload functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🧪 Testing Automatic Upload and Service Restart${NC}"
echo "=================================================="

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

# Test 1: Check current backend health
print_status "Test 1: Checking current backend health..."
if curl -s http://103.215.159.51:8000/health > /dev/null; then
    print_success "Backend is healthy"
else
    print_error "Backend is not responding"
    exit 1
fi

# Test 2: Check current services
print_status "Test 2: Checking current services..."
ssh backend-server 'systemctl status ai-messaging-backend.service --no-pager' | head -5
ssh backend-server 'ps aux | grep celery | grep -v grep | wc -l' | xargs echo "Celery workers running:"

# Test 3: Create a test file
print_status "Test 3: Creating test file..."
TEST_FILE="test_auto_upload_$(date +%s).py"
echo "# Test file for automatic upload - $(date)" > "$TEST_FILE"
echo "print('Hello from automatic upload test!')" >> "$TEST_FILE"
print_success "Created test file: $TEST_FILE"

# Test 4: Upload the test file
print_status "Test 4: Uploading test file..."
mkdir -p toUpload
cp "$TEST_FILE" toUpload/
./upload-to-server.sh --staging-dir toUpload --no-backup

# Test 5: Verify file was uploaded
print_status "Test 5: Verifying file upload..."
if ssh backend-server "cd /home/xb3353/Automated-AI-Messaging-Tool-Backend && ls -la $TEST_FILE"; then
    print_success "File uploaded successfully"
else
    print_error "File upload failed"
fi

# Test 6: Check if services restarted
print_status "Test 6: Checking if services restarted..."
sleep 2
if curl -s http://103.215.159.51:8000/health > /dev/null; then
    print_success "Backend is still healthy after restart"
else
    print_warning "Backend may have issues after restart"
fi

# Test 7: Clean up
print_status "Test 7: Cleaning up test files..."
rm -f "$TEST_FILE"
rm -rf toUpload
ssh backend-server "cd /home/xb3353/Automated-AI-Messaging-Tool-Backend && rm -f $TEST_FILE"
print_success "Cleanup completed"

# Test 8: Show final status
print_status "Test 8: Final service status..."
echo ""
echo -e "${PURPLE}📊 Final Status:${NC}"
echo "=================="
curl -s http://103.215.159.51:8000/health | python3 -m json.tool
echo ""
ssh backend-server 'systemctl status ai-messaging-backend.service --no-pager | head -3'
echo ""
ssh backend-server 'ps aux | grep celery | grep -v grep | wc -l' | xargs echo "Celery workers:"

echo ""
print_success "Automatic upload test completed!"
echo ""
echo -e "${PURPLE}🎯 Next Steps:${NC}"
echo "1. Run: ./watch-and-upload.sh"
echo "2. Edit any file in your project"
echo "3. Watch it upload and restart automatically!"
echo ""
echo -e "${YELLOW}💡 Tip: The file watcher will monitor for changes and upload them automatically${NC}" 