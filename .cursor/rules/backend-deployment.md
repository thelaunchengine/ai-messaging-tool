# Backend Deployment Guide

## 🚀 ECS Backend Deployment Process

### **Current Architecture:**
- **Frontend**: EC2 Instance (`34.195.237.115:3000`)
- **Backend**: ECS Fargate (`production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001`)
- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis

### **Deployment Methods:**

#### **Method 1: GitHub Actions (Recommended)**
```bash
# 1. Make changes to backend code
cd /Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Backend

# 2. Commit and push to trigger deployment
git add .
git commit -m "Update backend functionality"
git push origin main

# 3. GitHub Actions automatically:
#    - Builds Docker image from complete EC2 code
#    - Pushes to ECR (957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-backend)
#    - Updates ECS service
#    - Verifies deployment with health check
```

#### **Method 2: Manual Docker Deployment**
```bash
# 1. Build Docker image from complete code
cd /Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Backend
docker build -t production-ai-messaging-backend:latest .

# 2. Tag for ECR
docker tag production-ai-messaging-backend:latest 957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-backend:latest

# 3. Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 957440525184.dkr.ecr.us-east-1.amazonaws.com

# 4. Push to ECR
docker push 957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-backend:latest

# 5. Force ECS deployment
aws ecs update-service --cluster production-ai-messaging-cluster --service production-ai-messaging-backend-service --force-new-deployment --region us-east-1
```

### **Key Files and Locations:**

#### **Backend Code:**
- **Local**: `/Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Backend/` (Complete 2,591 lines)
- **EC2**: `/home/ubuntu/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend/` (Complete 2,591 lines)
- **ECS**: Containerized version from ECR

#### **Frontend Code:**
- **Local**: `/Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Frontend/`
- **EC2**: `/home/ubuntu/ai-messaging-tool/Automated-AI-Messaging-Tool-Frontend/`

### **Environment Variables:**

#### **Backend (ECS):**
```bash
DATABASE_URL=postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging
REDIS_URL=redis://production-ai-messaging-redis.cmpkwkuqu30h.cache.amazonaws.com:6379
CORS_ORIGINS=["http://34.195.237.115:3000", "http://localhost:3000", "http://localhost:3001"]
```

#### **Frontend (EC2):**
```bash
PYTHON_API_URL=http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001
NEXT_PUBLIC_PYTHON_BACKEND_URL=http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001
```

### **Health Check Endpoints:**
- **ECS Backend**: `http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001/api/health`
- **EC2 Frontend**: `http://34.195.237.115:3000/api/test-backend`

### **Troubleshooting:**

#### **Backend Issues:**
```bash
# Check ECS service status
aws ecs describe-services --cluster production-ai-messaging-cluster --services production-ai-messaging-backend-service --region us-east-1

# Check ECS task logs
aws logs get-log-events --log-group-name /ecs/production-ai-messaging-backend --log-stream-name <task-id> --region us-east-1

# Test backend directly
curl -f http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001/api/health
```

#### **Frontend Issues:**
```bash
# SSH to EC2
ssh -i ~/.ssh/ai-messaging-frontend-key.pem ubuntu@34.195.237.115

# Check PM2 status
pm2 status

# Restart frontend
cd /home/ubuntu/ai-messaging-tool/Automated-AI-Messaging-Tool-Frontend
pm2 restart frontend

# Check frontend logs
pm2 logs frontend
```

### **Important Notes:**

1. **Always use complete EC2 code** (2,591 lines) for Docker builds
2. **ECS account ID**: `957440525184` (not 123456789012)
3. **Health endpoint**: `/api/health` (not `/health`)
4. **Port**: ECS backend runs on port 8001
5. **CORS**: Must include EC2 frontend URL in allowed origins

### **GitHub Actions Workflows:**
- **Backend**: `.github/workflows/deploy-backend-to-ecs.yml`
- **Frontend**: `.github/workflows/deploy-frontend-to-ec2.yml`

### **Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `EC2_SSH_KEY`

### **Quick Commands:**
```bash
# Test backend health
curl http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001/api/health

# Test frontend-backend connection
curl http://34.195.237.115:3000/api/test-backend

# Force ECS deployment
aws ecs update-service --cluster production-ai-messaging-cluster --service production-ai-messaging-backend-service --force-new-deployment --region us-east-1
```
