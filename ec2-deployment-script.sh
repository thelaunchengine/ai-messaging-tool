#!/bin/bash

# EC2 Application Deployment Script
echo "🚀 Starting EC2 Application Deployment..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Node.js 18
echo "📦 Installing Node.js 18..."
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Install PM2 globally
echo "📦 Installing PM2..."
sudo npm install -g pm2

# Install Nginx
echo "🌐 Installing Nginx..."
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /var/www/ai-messaging-tool
sudo chown ec2-user:ec2-user /var/www/ai-messaging-tool
cd /var/www/ai-messaging-tool

# Install Git
echo "📦 Installing Git..."
sudo yum install -y git

# Clone the repository
echo "📥 Cloning application repository..."
git clone https://github.com/thelaunchengine/ai-messaging-tool.git .

# Set up environment variables
echo "⚙️ Setting up environment variables..."
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging

# NextAuth Configuration
NEXTAUTH_SECRET=your-nextauth-secret-key-here
NEXTAUTH_URL=http://34.234.90.48

# AI Model Configuration
GEMINI_API_KEY=AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I

# Redis Configuration
REDIS_URL=redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379

# Python Backend Configuration
PYTHON_BACKEND_URL=http://34.234.90.48:8000
NEXT_PUBLIC_PYTHON_BACKEND_URL=http://34.234.90.48:8000

# Base URL
NEXT_PUBLIC_BASE_URL=http://34.234.90.48

# Environment
NODE_ENV=production
PORT=3000
EOF

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd Automated-AI-Messaging-Tool-Frontend
npm install

# Build frontend
echo "🔨 Building frontend..."
npm run build

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd ../Automated-AI-Messaging-Tool-Backend
pip3 install -r requirements.txt

# Create PM2 ecosystem file
echo "⚙️ Creating PM2 ecosystem configuration..."
cat > ../ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'ai-messaging-frontend',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Frontend',
      script: 'npm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXTAUTH_URL: 'http://34.234.90.48',
        NEXTAUTH_SECRET: 'your-nextauth-secret-key-here',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379',
        NEXT_PUBLIC_BASE_URL: 'http://34.234.90.48',
        NEXT_PUBLIC_PYTHON_BACKEND_URL: 'http://34.234.90.48:8000'
      }
    },
    {
      name: 'ai-messaging-backend',
      cwd: '/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend',
      script: 'python3',
      args: 'main.py',
      env: {
        PYTHON_API_URL: 'http://34.234.90.48:8000',
        DATABASE_URL: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging',
        REDIS_URL: 'redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379',
        GEMINI_API_KEY: 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I'
      }
    }
  ]
};
EOF

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo cat > /etc/nginx/conf.d/ai-messaging-tool.conf << 'EOF'
server {
    listen 80;
    server_name 34.234.90.48;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Test Nginx configuration
echo "🔍 Testing Nginx configuration..."
sudo nginx -t

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

# Start applications with PM2
echo "🚀 Starting applications with PM2..."
cd /var/www/ai-messaging-tool
pm2 start ecosystem.config.js

# Save PM2 configuration
echo "💾 Saving PM2 configuration..."
pm2 save
pm2 startup

echo "✅ Deployment completed successfully!"
echo "🌐 Application should be available at: http://34.234.90.48"
echo "📊 Check status with: pm2 status"
echo "📝 View logs with: pm2 logs"
