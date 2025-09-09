# AI Messaging Tool

A full-stack application that automates website scraping, AI message generation, and contact form submissions.

## 🏗️ Architecture

- **Frontend**: Next.js (React) - Port 3000
- **Backend**: FastAPI (Python) - Port 8000
- **Database**: PostgreSQL (AWS RDS)
- **Cache**: Redis (AWS ElastiCache)
- **Storage**: S3 buckets
- **Deployment**: AWS ECS Fargate
- **Infrastructure**: AWS CloudFormation

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker
- AWS CLI configured

### Local Development

1. **Backend Setup**:
   ```bash
   cd Automated-AI-Messaging-Tool-Backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

2. **Frontend Setup**:
   ```bash
   cd Automated-AI-Messaging-Tool-Frontend
   npm install
   npm run dev
   ```

### AWS Deployment

The application is deployed using AWS CloudFormation templates in the `cloudformation/` directory:

1. **Step 1**: ECS Cluster
2. **Step 2**: Application Load Balancer
3. **Step 3**: Target Groups
4. **Step 4**: Backend ECS Service
5. **Step 5**: Frontend ECS Service

## 📁 Project Structure

```
ai-messaging-tool/
├── Automated-AI-Messaging-Tool-Backend/    # Python FastAPI backend
├── Automated-AI-Messaging-Tool-Frontend/   # Next.js frontend
├── cloudformation/                          # AWS infrastructure templates
├── .github/workflows/                       # GitHub Actions CI/CD
└── src/                                    # Additional utilities
```

## 🔧 Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_HOST`: Redis endpoint
- `S3_BUCKET`: S3 bucket name
- `GEMINI_API_KEY`: Google AI API key

### Frontend
- `NEXT_PUBLIC_BACKEND_URL`: Backend API URL
- `NEXTAUTH_URL`: Authentication URL
- `NEXTAUTH_SECRET`: Authentication secret

## 🚀 Deployment

The application is automatically deployed to AWS using GitHub Actions when code is pushed to the `main` branch.

### Manual Deployment

1. **Deploy Infrastructure**:
   ```bash
   aws cloudformation create-stack --stack-name ai-messaging-step1-cluster --template-body file://cloudformation/step1-ecs-cluster.yaml
   ```

2. **Deploy Services**:
   ```bash
   aws cloudformation create-stack --stack-name ai-messaging-step4-backend --template-body file://cloudformation/step4-backend-service.yaml
   ```

## 📊 Monitoring

- **CloudWatch Logs**: Application logs
- **ECS Console**: Service status and health
- **Load Balancer**: Health checks and metrics

## 🔗 URLs

- **Frontend**: http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:3000
- **Backend API**: http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8000
- **Health Check**: http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8000/health

## 📝 License

Private project - All rights reserved.
