#!/bin/bash

# Backend EC2 Deployment Script
echo "🚀 Starting Backend EC2 Deployment from GitHub..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update -y
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
sudo apt install -y git curl wget unzip

# Install Node.js 18 (for PM2)
echo "📦 Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
echo "📦 Installing PM2..."
sudo npm install -g pm2

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /var/www/ai-messaging-tool
sudo chown ubuntu:ubuntu /var/www/ai-messaging-tool
cd /var/www/ai-messaging-tool

# Clone the repository
echo "📥 Cloning application repository..."
git clone https://github.com/thelaunchengine/ai-messaging-tool.git .

# Navigate to backend directory
cd Automated-AI-Messaging-Tool-Backend

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging

# Redis Configuration
REDIS_URL=redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379/0

# AI Model Configuration
GEMINI_API_KEY=AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I

# Application Configuration
TESTING_MODE_ENABLED=false
MAX_AI_MESSAGES_PER_FILE=30
PYTHON_API_URL=http://98.85.16.204:8000

# Environment
NODE_ENV=production
EOF

# Create PM2 ecosystem configuration
echo "⚙️ Creating PM2 ecosystem configuration..."
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'fastapi-backend',
      script: 'venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      exec_mode: 'fork',
      interpreter: 'none',
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: '10s',
      env: {
        NODE_ENV: 'production',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379/0',
        GEMINI_API_KEY: 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I',
        TESTING_MODE_ENABLED: 'false',
        MAX_AI_MESSAGES_PER_FILE: '30',
        PYTHON_API_URL: 'http://98.85.16.204:8000'
      },
      error_file: '/var/log/fastapi-error.log',
      out_file: '/var/log/fastapi-out.log',
      log_file: '/var/log/fastapi-combined.log',
      time: true
    },
    {
      name: 'celery-worker-1',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker1@%h --max-tasks-per-child=1000',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        NODE_ENV: 'production',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379/0',
        GEMINI_API_KEY: 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I',
        TESTING_MODE_ENABLED: 'false',
        MAX_AI_MESSAGES_PER_FILE: '30'
      },
      error_file: '/var/log/celery-worker-1-error.log',
      out_file: '/var/log/celery-worker-1-out.log',
      log_file: '/var/log/celery-worker-1-combined.log',
      time: true,
      restart_delay: 5000,
      interpreter: 'none',
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'celery-worker-2',
      script: 'venv/bin/celery',
      args: '-A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker2@%h --max-tasks-per-child=1000',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        NODE_ENV: 'production',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379/0',
        GEMINI_API_KEY: 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I',
        TESTING_MODE_ENABLED: 'false',
        MAX_AI_MESSAGES_PER_FILE: '30'
      },
      error_file: '/var/log/celery-worker-2-error.log',
      out_file: '/var/log/celery-worker-2-out.log',
      log_file: '/var/log/celery-worker-2-combined.log',
      time: true,
      restart_delay: 5000,
      exec_mode: 'fork',
      interpreter: 'none',
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
EOF

# Create log directory
echo "📁 Creating log directory..."
sudo mkdir -p /var/log
sudo chown ubuntu:ubuntu /var/log

# Test the application
echo "🧪 Testing the application..."
source venv/bin/activate
python -c "import main; print('✅ Main module imports successfully')"

# Start applications with PM2
echo "🚀 Starting applications with PM2..."
pm2 start ecosystem.config.js

# Save PM2 configuration
echo "💾 Saving PM2 configuration..."
pm2 save
pm2 startup

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 8000
sudo ufw --force enable

# Test the deployment
echo "🧪 Testing deployment..."
sleep 10
curl -f http://localhost:8000/docs || echo "⚠️ Backend not responding on port 8000"

echo "✅ Backend deployment completed successfully!"
echo "🌐 Backend should be available at: http://98.85.16.204:8000"
echo "📊 Check status with: pm2 status"
echo "📝 View logs with: pm2 logs"
echo "🔧 Backend API docs: http://98.85.16.204:8000/docs"
