#!/bin/bash

# Setup Passwordless Sudo for Backend Service Restarts
# This script will configure sudo to allow service restarts without password

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🔧 Setting up Passwordless Sudo for Service Restarts${NC}"
echo "========================================================"

# Configuration
SERVER_HOST="103.215.159.51"
SERVER_USER="xb3353"
SERVICE_NAME="ai-messaging-backend"
CELERY_SERVICE_NAME="ai-messaging-celery"

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

# Step 1: Create sudoers entries
print_status "Step 1: Creating sudoers entries for service restarts..."

SUDOERS_ENTRIES="
# AI Messaging Backend Service Restart Permissions
$SERVER_USER ALL=NOPASSWD: /bin/systemctl restart $SERVICE_NAME.service
$SERVER_USER ALL=NOPASSWD: /bin/systemctl status $SERVICE_NAME.service
$SERVER_USER ALL=NOPASSWD: /bin/systemctl restart $CELERY_SERVICE_NAME.service
$SERVER_USER ALL=NOPASSWD: /bin/systemctl status $CELERY_SERVICE_NAME.service
$SERVER_USER ALL=NOPASSWD: /bin/systemctl stop $SERVICE_NAME.service
$SERVER_USER ALL=NOPASSWD: /bin/systemctl start $SERVICE_NAME.service
$SERVER_USER ALL=NOPASSWD: /bin/systemctl stop $CELERY_SERVICE_NAME.service
$SERVER_USER ALL=NOPASSWD: /bin/systemctl start $CELERY_SERVICE_NAME.service
"

echo ""
echo -e "${YELLOW}📋 Copy and paste these commands on your server:${NC}"
echo "========================================================"
echo ""
echo -e "${CYAN}1. SSH into your server:${NC}"
echo "   ssh $SERVER_USER@$SERVER_HOST"
echo ""
echo -e "${CYAN}2. Edit sudoers file:${NC}"
echo "   sudo visudo"
echo ""
echo -e "${CYAN}3. Add these lines at the end of the file:${NC}"
echo "$SUDOERS_ENTRIES"
echo ""
echo -e "${CYAN}4. Save and exit (Ctrl+O, Enter, Ctrl+X)${NC}"
echo ""

# Step 2: Create Celery systemd service
print_status "Step 2: Creating Celery systemd service..."

CELERY_SERVICE_CONTENT="[Unit]
Description=AI Messaging Celery Worker
After=network.target

[Service]
Type=simple
User=$SERVER_USER
Group=$SERVER_USER
WorkingDirectory=/home/$SERVER_USER/Automated-AI-Messaging-Tool-Backend
Environment=PATH=/home/$SERVER_USER/Automated-AI-Messaging-Tool-Backend/venv/bin
ExecStart=/home/$SERVER_USER/Automated-AI-Messaging-Tool-Backend/venv/bin/celery -A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker@%h --max-tasks-per-child=1000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"

echo -e "${YELLOW}📋 Create Celery systemd service:${NC}"
echo "========================================================"
echo ""
echo -e "${CYAN}5. Create Celery service file:${NC}"
echo "   sudo nano /etc/systemd/system/$CELERY_SERVICE_NAME.service"
echo ""
echo -e "${CYAN}6. Paste this content:${NC}"
echo "$CELERY_SERVICE_CONTENT"
echo ""
echo -e "${CYAN}7. Save and exit (Ctrl+O, Enter, Ctrl+X)${NC}"
echo ""

# Step 3: Enable and start services
print_status "Step 3: Enable and start services..."

echo -e "${YELLOW}📋 Enable and start the Celery service:${NC}"
echo "========================================================"
echo ""
echo -e "${CYAN}8. Reload systemd and enable services:${NC}"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable $CELERY_SERVICE_NAME.service"
echo "   sudo systemctl start $CELERY_SERVICE_NAME.service"
echo ""
echo -e "${CYAN}9. Check service status:${NC}"
echo "   sudo systemctl status $CELERY_SERVICE_NAME.service"
echo ""

# Step 4: Test passwordless sudo
print_status "Step 4: Test passwordless sudo..."

echo -e "${YELLOW}📋 Test passwordless sudo (run from your local machine):${NC}"
echo "========================================================"
echo ""
echo -e "${CYAN}10. Test backend restart:${NC}"
echo "   ssh backend-server 'sudo systemctl restart $SERVICE_NAME.service'"
echo ""
echo -e "${CYAN}11. Test Celery restart:${NC}"
echo "   ssh backend-server 'sudo systemctl restart $CELERY_SERVICE_NAME.service'"
echo ""
echo -e "${CYAN}12. Check service status:${NC}"
echo "   ssh backend-server 'sudo systemctl status $SERVICE_NAME.service'"
echo "   ssh backend-server 'sudo systemctl status $CELERY_SERVICE_NAME.service'"
echo ""

# Step 5: Update upload scripts
print_status "Step 5: Update upload scripts to use systemd..."

echo -e "${YELLOW}📋 Your upload scripts will now automatically restart services!${NC}"
echo "========================================================"
echo ""
echo -e "${GREEN}✅ After completing the above steps:${NC}"
echo "   - Run: ./watch-and-upload.sh"
echo "   - Edit any file"
echo "   - It will automatically upload and restart services!"
echo ""

print_success "Setup instructions generated!"
echo ""
echo -e "${PURPLE}🎯 Next Steps:${NC}"
echo "1. Follow the commands above on your server"
echo "2. Test the passwordless sudo commands"
echo "3. Start the file watcher: ./watch-and-upload.sh"
echo "4. Edit files and watch them upload automatically!"
echo "" 