#!/bin/bash

# Quick Deploy Script for AI Messaging Tool
# This script builds and deploys the application to AWS ECS

set -e

echo "🚀 Starting quick deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="us-east-1"
ECR_REGISTRY="957440525184.dkr.ecr.us-east-1.amazonaws.com"
BACKEND_IMAGE="production-ai-messaging-backend"
FRONTEND_IMAGE="production-ai-messaging-frontend"
CLUSTER_NAME="production-ai-messaging-cluster"

echo -e "${YELLOW}Step 1: Building Docker images...${NC}"

# Build backend image
echo "Building backend image..."
cd Automated-AI-Messaging-Tool-Backend
docker build --no-cache -t ai-messaging-backend:latest .
docker tag ai-messaging-backend:latest $ECR_REGISTRY/$BACKEND_IMAGE:latest
cd ..

# Build frontend image
echo "Building frontend image..."
cd Automated-AI-Messaging-Tool-Frontend
docker build --no-cache -t ai-messaging-frontend:latest .
docker tag ai-messaging-frontend:latest $ECR_REGISTRY/$FRONTEND_IMAGE:latest
cd ..

echo -e "${YELLOW}Step 2: Pushing images to ECR...${NC}"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Push images
echo "Pushing backend image..."
docker push $ECR_REGISTRY/$BACKEND_IMAGE:latest

echo "Pushing frontend image..."
docker push $ECR_REGISTRY/$FRONTEND_IMAGE:latest

echo -e "${YELLOW}Step 3: Updating ECS services...${NC}"

# Update backend service
echo "Updating backend service..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service production-ai-messaging-backend-service \
  --force-new-deployment

# Update frontend service (if it exists)
echo "Updating frontend service..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service production-ai-messaging-frontend-service \
  --force-new-deployment || echo "Frontend service not found yet"

echo -e "${YELLOW}Step 4: Waiting for deployment to complete...${NC}"

# Wait for backend service to be stable
aws ecs wait services-stable \
  --cluster $CLUSTER_NAME \
  --services production-ai-messaging-backend-service

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"

# Get load balancer URL
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[?contains(LoadBalancerName, `ai-messaging`)].DNSName' \
  --output text)

echo -e "${GREEN}🚀 Application URLs:${NC}"
echo "Frontend: http://$ALB_DNS:3000"
echo "Backend: http://$ALB_DNS:8000"
echo "Health Check: http://$ALB_DNS:8000/health"

echo -e "${GREEN}🎉 Deployment complete!${NC}"
