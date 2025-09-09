#!/bin/bash

# DEPLOYMENT SCRIPT FOR OPTIMIZATIONS
# This script deploys all the optimizations

echo "🚀 Deploying optimizations..."

# Step 1: Stop existing services
echo "📋 Step 1: Stopping existing services..."
pm2 stop all

# Step 2: Apply database updates
echo "🗄️  Step 2: Applying database updates..."
psql -U postgres -d ai_messaging_tool -f database_updates.sql

# Step 3: Update PM2 configuration
echo "⚙️  Step 3: Updating PM2 configuration..."
pm2 delete all
pm2 start ecosystem_optimized.config.js

# Step 4: Start services with new configuration
echo "🔄 Step 4: Starting services with new configuration..."
pm2 start ecosystem_optimized.config.js

# Step 5: Save PM2 configuration
echo "💾 Step 5: Saving PM2 configuration..."
pm2 save

# Step 6: Show status
echo "📊 Step 6: Showing service status..."
pm2 status

echo "✅ Deployment completed successfully!"
echo "🔄 Services are now running with optimizations"
echo "📊 Monitor performance with: pm2 logs"
