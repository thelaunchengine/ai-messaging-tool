#!/bin/bash

# SIMPLIFIED DEPLOYMENT SCRIPT FOR OPTIMIZATIONS
# This script deploys the optimized services without database changes

echo "🚀 Deploying optimizations (simplified)..."

# Step 1: Stop existing services
echo "📋 Step 1: Stopping existing services..."
pm2 stop all 2>/dev/null || echo "No services to stop"

# Step 2: Start services with optimized configuration
echo "🔄 Step 2: Starting services with optimized configuration..."
pm2 start ecosystem_optimized.config.js

# Step 3: Save PM2 configuration
echo "💾 Step 3: Saving PM2 configuration..."
pm2 save

# Step 4: Show status
echo "📊 Step 4: Showing service status..."
pm2 status

echo "✅ Deployment completed successfully!"
echo "🔄 Services are now running with optimizations"
echo "📊 Monitor performance with: pm2 logs"
echo ""
echo "🔧 Key optimizations applied:"
echo "   - Reduced batch size from 44 to 15 websites"
echo "   - Parallel processing of 10 websites simultaneously"
echo "   - 5-minute timeout per website"
echo "   - 4 Celery workers with 8 concurrency each (32 total concurrent tasks)"
echo "   - Resource monitoring and progress tracking"
