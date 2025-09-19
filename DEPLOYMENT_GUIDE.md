# GitHub Actions Deployment Guide

## 🚀 Automated Deployment Setup

This guide explains how to set up automated deployment from GitHub to AWS ECS (backend) and EC2 (frontend).

## 📋 Prerequisites

### 1. GitHub Secrets Required

Add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

#### AWS Credentials (for ECS deployment):
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

#### EC2 Credentials (for frontend deployment):
- `EC2_SSH_KEY`: Your private SSH key for EC2 access

### 2. Repository Structure
```
├── .github/
│   └── workflows/
│       ├── deploy-backend-to-ecs.yml
│       └── deploy-frontend-to-ec2.yml
├── Automated-AI-Messaging-Tool-Backend/
│   ├── main.py (complete production code)
│   ├── Dockerfile
│   └── requirements.txt
└── Automated-AI-Messaging-Tool-Frontend/
    ├── package.json
    └── next.config.js
```

## 🔄 How It Works

### Backend Deployment (EC2 → ECS)
1. **Trigger**: Push to `main` branch with changes in `Automated-AI-Messaging-Tool-Backend/`
2. **Process**:
   - Builds Docker image from complete EC2 code
   - Pushes to ECR (`957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-backend`)
   - Updates ECS service with new image
   - Verifies deployment with health check

### Frontend Deployment (Local → EC2)
1. **Trigger**: Push to `main` branch with changes in `Automated-AI-Messaging-Tool-Frontend/`
2. **Process**:
   - Builds Next.js application
   - Deploys to EC2 via SSH
   - Restarts PM2 process
   - Verifies deployment

## 🛠️ Setup Steps

### Step 1: Push Complete Code to GitHub
```bash
cd /Users/apple/Documents/aimsg
git add .
git commit -m "Sync complete EC2 code and add GitHub Actions workflows"
git push origin main
```

### Step 2: Configure GitHub Secrets
1. Go to your GitHub repository
2. Navigate to `Settings > Secrets and variables > Actions`
3. Add the required secrets listed above

### Step 3: Test Deployment
1. Make a small change to trigger deployment
2. Check the `Actions` tab in GitHub to monitor progress
3. Verify deployments are working

## 🔧 Environment Configuration

### Backend (ECS)
- **Load Balancer**: `production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001`
- **Health Check**: `/api/health`
- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis

### Frontend (EC2)
- **URL**: `http://34.195.237.115:3000`
- **Process Manager**: PM2
- **Backend API**: Points to ECS load balancer

## 📊 Current Status

| Component | Environment | Status | Code Version |
|-----------|-------------|--------|--------------|
| Backend | EC2 | ✅ Running | Complete (2,591 lines) |
| Backend | ECS | ✅ Running | Complete (2,591 lines) |
| Backend | Local | ✅ Synced | Complete (2,591 lines) |
| Frontend | EC2 | ✅ Running | Latest |
| Frontend | Local | ✅ Ready | Latest |

## 🎯 Next Steps

1. **Push to GitHub**: Commit and push the complete code
2. **Configure Secrets**: Add AWS and EC2 credentials to GitHub
3. **Test Deployment**: Make a change and verify automated deployment
4. **Monitor**: Use GitHub Actions dashboard to track deployments

## 🔍 Troubleshooting

### Common Issues:
1. **ECR Push Fails**: Check AWS credentials and permissions
2. **ECS Deployment Fails**: Verify task definition and service configuration
3. **Frontend Deployment Fails**: Check EC2 SSH key and PM2 configuration
4. **Health Check Fails**: Ensure load balancer security groups allow port 8001

### Manual Deployment Commands:
```bash
# Backend to ECS
aws ecs update-service --cluster production-ai-messaging-cluster --service production-ai-messaging-backend-service --force-new-deployment

# Frontend to EC2
ssh -i ~/.ssh/ai-messaging-frontend-key.pem ubuntu@34.195.237.115 "cd /home/ubuntu/ai-messaging-tool/Automated-AI-Messaging-Tool-Frontend && git pull && npm run build && pm2 restart frontend"
```
