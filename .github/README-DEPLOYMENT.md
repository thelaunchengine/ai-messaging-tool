# 🚀 GitHub Actions CI/CD Setup for AI Messaging Tool

This repository is configured with automated deployment to AWS ECS using GitHub Actions.

## 📋 Prerequisites

1. **AWS Account** with ECS, ECR, and IAM permissions
2. **GitHub Repository** with Actions enabled
3. **AWS Secrets** configured in GitHub

## 🔧 Setup Instructions

### 1. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions, and add these secrets:

```
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
```

### 2. Create ECR Repositories

The workflows will automatically create ECR repositories if they don't exist:
- `ai-messaging-frontend`
- `ai-messaging-backend`

### 3. Create CloudWatch Log Groups

```bash
aws logs create-log-group --log-group-name /ecs/ai-messaging-frontend
aws logs create-log-group --log-group-name /ecs/ai-messaging-backend
```

### 4. Deploy Infrastructure

Make sure your AWS infrastructure is deployed using the CloudFormation templates in the `cloudformation/` directory.

## 🚀 How It Works

### Automatic Deployment

1. **Push to main branch** triggers deployment
2. **Docker images** are built and pushed to ECR
3. **ECS services** are updated with new images
4. **Zero-downtime deployment** using rolling updates

### Manual Deployment

You can also trigger deployments manually:
1. Go to Actions tab in GitHub
2. Select "Deploy Frontend" or "Deploy Backend"
3. Click "Run workflow"

## 📁 File Structure

```
.github/workflows/
├── deploy-frontend.yml    # Frontend deployment workflow
└── deploy-backend.yml     # Backend deployment workflow

cloudformation/task-definitions/
├── frontend-task-definition.json
└── backend-task-definition.json
```

## 🔍 Monitoring

- **GitHub Actions**: Check the Actions tab for deployment status
- **AWS ECS**: Monitor service health in AWS Console
- **CloudWatch**: View application logs and metrics

## 🛠️ Troubleshooting

### Common Issues

1. **ECR Repository Not Found**
   - The workflow will create repositories automatically
   - Ensure AWS credentials have ECR permissions

2. **ECS Service Update Failed**
   - Check ECS service status in AWS Console
   - Verify task definition is valid

3. **Docker Build Failed**
   - Check Dockerfile syntax
   - Ensure all dependencies are included

### Debug Steps

1. Check GitHub Actions logs
2. Verify AWS credentials are correct
3. Ensure ECS cluster and services exist
4. Check CloudWatch logs for application errors

## 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Review AWS CloudWatch logs
3. Verify your AWS infrastructure is properly configured
