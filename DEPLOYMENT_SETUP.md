# AWS ECS Deployment Setup

## 🚀 GitHub Actions Deployment

This repository is configured for automated deployment to AWS ECS using GitHub Actions.

### Prerequisites

1. **AWS Account** with ECS, ECR, RDS, and ElastiCache services
2. **GitHub Repository** with the following secrets configured:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

### AWS Resources Required

- **ECS Cluster**: `production-ai-messaging-cluster`
- **ECR Repositories**:
  - `production-ai-messaging-frontend`
  - `production-ai-messaging-backend`
  - `production-ai-messaging-worker`
- **RDS Database**: `production-ai-messaging-db`
- **ElastiCache Redis**: `production-ai-messaging-redis-001`
- **Application Load Balancer**: `production-ai-messaging-alb`

### Environment Configuration

The application is configured to use AWS services:

#### Frontend (.env)
- Database: AWS RDS PostgreSQL
- Backend API: AWS ALB
- Base URL: AWS ALB

#### Backend (.env)
- Database: AWS RDS PostgreSQL
- Redis: AWS ElastiCache
- AI API: Gemini

### Deployment Process

1. **Push to main/master branch** triggers deployment
2. **GitHub Actions** builds Docker images
3. **Images pushed** to ECR
4. **ECS services updated** with new images
5. **Health checks** ensure deployment success

### Manual Deployment

If you need to deploy manually:

```bash
# Build and push images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 957440525184.dkr.ecr.us-east-1.amazonaws.com

# Frontend
cd working-code-backup/frontend
docker build -t 957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-frontend:latest .
docker push 957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-frontend:latest

# Backend
cd ../backend
docker build -t 957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-backend:latest .
docker push 957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-backend:latest

# Worker
docker build -f Dockerfile.worker -t 957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-worker:latest .
docker push 957440525184.dkr.ecr.us-east-1.amazonaws.com/production-ai-messaging-worker:latest

# Update ECS services
aws ecs update-service --cluster production-ai-messaging-cluster --service production-ai-messaging-frontend-service --force-new-deployment
aws ecs update-service --cluster production-ai-messaging-cluster --service production-ai-messaging-backend-service --force-new-deployment
```

### Monitoring

- **ECS Console**: Monitor service health and logs
- **CloudWatch**: Application logs and metrics
- **ALB**: Load balancer health and traffic

### Troubleshooting

1. **Check ECS service logs** in CloudWatch
2. **Verify security groups** allow traffic
3. **Check database connectivity** from ECS tasks
4. **Verify environment variables** are correct
