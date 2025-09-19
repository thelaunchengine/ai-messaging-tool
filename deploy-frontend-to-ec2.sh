#!/bin/bash

# Deploy Frontend to AWS EC2 Instance
# Frontend Instance: i-0a9d06c31b8a13234 (34.195.237.115)

echo "🚀 Starting Frontend Deployment to AWS EC2..."

# Configuration
EC2_HOST="34.195.237.115"
EC2_USER="ubuntu"
EC2_KEY="~/.ssh/ai-messaging-frontend-key.pem"
FRONTEND_DIR="/Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Frontend"
REMOTE_DIR="/home/ubuntu/ai-messaging-tool/Automated-AI-Messaging-Tool-Frontend"

echo "📦 Building frontend locally..."
cd "$FRONTEND_DIR"
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Exiting."
    exit 1
fi

echo "✅ Local build successful"

echo "🔄 Syncing files to EC2..."
rsync -avz --delete \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude '.next/cache' \
    --exclude 'logs' \
    --exclude 'temp_upload' \
    --exclude 'uploads' \
    -e "ssh -i $EC2_KEY" \
    "$FRONTEND_DIR/" \
    "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

if [ $? -ne 0 ]; then
    echo "❌ Sync failed. Exiting."
    exit 1
fi

echo "✅ Files synced successfully"

echo "🔧 Installing dependencies and restarting service on EC2..."
ssh -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << 'EOF'
cd /home/ubuntu/ai-messaging-tool/Automated-AI-Messaging-Tool-Frontend

echo "Installing dependencies..."
npm install

echo "Building production version..."
npm run build

echo "Restarting PM2 process..."
pm2 restart frontend

echo "Checking status..."
pm2 list

echo "✅ Deployment completed!"
EOF

echo "🎉 Frontend deployment completed successfully!"
echo "🌐 Frontend should be available at: http://34.195.237.115:3000"
