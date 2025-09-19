#!/bin/bash

# 🚀 AI Messaging Application Deployment Script
# This script automates the deployment of both Python backend and Next.js frontend

set -e  # Exit on any error

echo "🚀 Starting AI Messaging Application Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
    exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential tools
print_status "Installing essential tools..."
sudo apt install -y curl wget git unzip build-essential software-properties-common

# Install Node.js 18.x
print_status "Installing Node.js 18.x..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify Node.js installation
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
print_success "Node.js $NODE_VERSION and npm $NPM_VERSION installed"

# Install Python 3.11
print_status "Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verify Python installation
PYTHON_VERSION=$(python3.11 --version)
print_success "Python $PYTHON_VERSION installed"

# Install PostgreSQL
print_status "Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Install Redis
print_status "Installing Redis..."
sudo apt install -y redis-server

# Start and enable Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install Nginx
print_status "Installing Nginx..."
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Create application directories
print_status "Creating application directories..."
sudo mkdir -p /opt/ai-messaging-backend
sudo mkdir -p /opt/ai-messaging-frontend
sudo chown $USER:$USER /opt/ai-messaging-backend
sudo chown $USER:$USER /opt/ai-messaging-frontend

# Setup Python Backend
print_status "Setting up Python backend..."
cd /opt/ai-messaging-backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup PostgreSQL database
print_status "Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE ai_messaging;" || print_warning "Database might already exist"
sudo -u postgres psql -c "CREATE USER ai_user WITH PASSWORD 'ai_messaging_password';" || print_warning "User might already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_messaging TO ai_user;"

# Initialize database schema
print_status "Initializing database schema..."
python database/init_db.py

# Create environment file
print_status "Creating environment configuration..."
cat > .env << EOF
# Database
DATABASE_URL=postgresql://ai_user:ai_messaging_password@localhost:5432/ai_messaging

# Redis
REDIS_URL=redis://localhost:6379/0

# AI API Keys
GEMINI_API_KEY=AIzaSyAktRAFpxfniqX0ZCFswTNKQh59alVeSGY

# CAPTCHA (optional)
CAPTCHA_API_KEY=your_2captcha_api_key

# Form Submission
SENDER_NAME=AI Messaging System
SENDER_EMAIL=admin@yourdomain.com
SENDER_PHONE=+1-555-123-4567
MESSAGE_SUBJECT=Business Inquiry
COMPANY_NAME=Your Company

# Server Configuration
PORT=8000
HOST=0.0.0.0
EOF

print_success "Backend environment configured"

# Setup Next.js Frontend
print_status "Setting up Next.js frontend..."
cd /opt/ai-messaging-frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

# Create environment file for frontend
print_status "Creating frontend environment configuration..."
cat > .env.local << EOF
# Backend URL
PYTHON_BACKEND_URL=http://localhost:8000

# Next.js Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-change-this-in-production

# Database (if using Prisma)
DATABASE_URL=postgresql://ai_user:ai_messaging_password@localhost:5432/ai_messaging
EOF

# Build frontend
print_status "Building Next.js application..."
npm run build

print_success "Frontend built successfully"

# Create systemd services
print_status "Creating systemd services..."

# Backend service
sudo tee /etc/systemd/system/ai-messaging-backend.service > /dev/null << EOF
[Unit]
Description=AI Messaging Backend
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-messaging-backend
Environment=PATH=/opt/ai-messaging-backend/venv/bin
ExecStart=/opt/ai-messaging-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Celery service
sudo tee /etc/systemd/system/ai-messaging-celery.service > /dev/null << EOF
[Unit]
Description=AI Messaging Celery Worker
After=network.target redis-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-messaging-backend
Environment=PATH=/opt/ai-messaging-backend/venv/bin
ExecStart=/opt/ai-messaging-backend/venv/bin/celery -A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
sudo tee /etc/systemd/system/ai-messaging-frontend.service > /dev/null << EOF
[Unit]
Description=AI Messaging Frontend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/ai-messaging-frontend
Environment=NODE_ENV=production
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
print_status "Setting application permissions..."
sudo chown -R www-data:www-data /opt/ai-messaging-backend
sudo chown -R www-data:www-data /opt/ai-messaging-frontend

# Create Nginx configuration
print_status "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/ai-messaging > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Upload files
    location /uploads/ {
        alias /opt/ai-messaging-backend/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/ai-messaging /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload systemd and start services
print_status "Starting services..."
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable ai-messaging-backend
sudo systemctl enable ai-messaging-celery
sudo systemctl enable ai-messaging-frontend

# Start services
sudo systemctl start ai-messaging-backend
sudo systemctl start ai-messaging-celery
sudo systemctl start ai-messaging-frontend

# Reload Nginx
sudo systemctl reload nginx

# Wait a moment for services to start
sleep 5

# Check service status
print_status "Checking service status..."
echo ""
echo "Service Status:"
echo "==============="

services=("ai-messaging-backend" "ai-messaging-celery" "ai-messaging-frontend" "nginx" "postgresql" "redis-server")

for service in "${services[@]}"; do
    if sudo systemctl is-active --quiet $service; then
        print_success "$service is running"
    else
        print_error "$service is not running"
    fi
done

echo ""
print_success "Deployment completed successfully!"
echo ""
echo "🌐 Application URLs:"
echo "   Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo "   Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "   API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "📋 Next Steps:"
echo "   1. Update environment variables in /opt/ai-messaging-backend/.env"
echo "   2. Update frontend environment in /opt/ai-messaging-frontend/.env.local"
echo "   3. Configure your domain name in Nginx configuration"
echo "   4. Set up SSL certificate with Certbot"
echo "   5. Monitor logs: sudo journalctl -u ai-messaging-backend -f"
echo ""
echo "🔧 Useful Commands:"
echo "   Check status: sudo systemctl status ai-messaging-backend"
echo "   View logs: sudo journalctl -u ai-messaging-backend -f"
echo "   Restart services: sudo systemctl restart ai-messaging-backend"
echo "   Test API: curl http://localhost:8000/health"
echo "" 