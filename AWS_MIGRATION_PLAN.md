# AWS Migration Plan - AI Messaging Tool
## Complete Step-by-Step Migration Guide

### 🎯 **Migration Overview**
This plan migrates your AI Messaging Tool from a single server to a scalable AWS cloud infrastructure using CloudFormation templates and manual deployment steps.

---

## 📋 **Phase 1: Infrastructure Foundation (Week 1)**

### **Step 1.1: Create VPC and Networking**
```bash
# Create VPC CloudFormation stack
aws cloudformation create-stack \
  --stack-name ai-messaging-vpc \
  --template-body file://cloudformation/vpc.yaml \
  --capabilities CAPABILITY_IAM

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name ai-messaging-vpc
```

**What this creates:**
- VPC with public/private subnets
- Internet Gateway and NAT Gateway
- Security Groups for all services
- Route tables and NACLs

### **Step 1.2: Create RDS Database**
```bash
# Create RDS CloudFormation stack
aws cloudformation create-stack \
  --stack-name ai-messaging-database \
  --template-body file://cloudformation/rds.yaml \
  --parameters ParameterKey=VPCStackName,ParameterValue=ai-messaging-vpc \
  --capabilities CAPABILITY_IAM

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name ai-messaging-database
```

**What this creates:**
- RDS PostgreSQL instance (db.t3.small)
- Multi-AZ deployment for high availability
- Automated backups and monitoring
- Security group for database access

### **Step 1.3: Create ElastiCache Redis**
```bash
# Create ElastiCache CloudFormation stack
aws cloudformation create-stack \
  --stack-name ai-messaging-cache \
  --template-body file://cloudformation/elasticache.yaml \
  --parameters ParameterKey=VPCStackName,ParameterValue=ai-messaging-vpc \
  --capabilities CAPABILITY_IAM

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name ai-messaging-cache
```

**What this creates:**
- ElastiCache Redis cluster (cache.t3.micro)
- Subnet group and security group
- Parameter group for optimization

### **Step 1.4: Create S3 Buckets**
```bash
# Create S3 CloudFormation stack
aws cloudformation create-stack \
  --stack-name ai-messaging-storage \
  --template-body file://cloudformation/s3.yaml \
  --capabilities CAPABILITY_IAM

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name ai-messaging-storage
```

**What this creates:**
- S3 bucket for file uploads
- S3 bucket for frontend static assets
- S3 bucket for backups
- Bucket policies and CORS configuration

---

## 🚀 **Phase 2: Container Infrastructure (Week 2)**

### **Step 2.1: Create ECR Repositories**
```bash
# Create ECR CloudFormation stack
aws cloudformation create-stack \
  --stack-name ai-messaging-ecr \
  --template-body file://cloudformation/ecr.yaml \
  --capabilities CAPABILITY_IAM

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name ai-messaging-ecr
```

**What this creates:**
- ECR repository for backend images
- ECR repository for frontend images
- Lifecycle policies for image cleanup

### **Step 2.2: Build and Push Docker Images**

#### **Backend Docker Image:**
```bash
# Navigate to backend directory
cd Automated-AI-Messaging-Tool-Backend

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build and push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 957440525184.dkr.ecr.us-east-1.amazonaws.com

docker build -t ai-messaging-backend .
docker tag ai-messaging-backend:latest 957440525184.dkr.ecr.us-east-1.amazonaws.com/ai-messaging-backend:latest
docker push 957440525184.dkr.ecr.us-east-1.amazonaws.com/ai-messaging-backend:latest
```

#### **Frontend Docker Image:**
```bash
# Navigate to frontend directory
cd Automated-AI-Messaging-Tool-Frontend

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
EOF

# Build and push image
docker build -t ai-messaging-frontend .
docker tag ai-messaging-frontend:latest 957440525184.dkr.ecr.us-east-1.amazonaws.com/ai-messaging-frontend:latest
docker push 957440525184.dkr.ecr.us-east-1.amazonaws.com/ai-messaging-frontend:latest
```

### **Step 2.3: Create ECS Cluster and Services**
```bash
# Create ECS CloudFormation stack
aws cloudformation create-stack \
  --stack-name ai-messaging-ecs \
  --template-body file://cloudformation/ecs.yaml \
  --parameters \
    ParameterKey=VPCStackName,ParameterValue=ai-messaging-vpc \
    ParameterKey=DatabaseStackName,ParameterValue=ai-messaging-database \
    ParameterKey=CacheStackName,ParameterValue=ai-messaging-cache \
    ParameterKey=StorageStackName,ParameterValue=ai-messaging-storage \
  --capabilities CAPABILITY_IAM

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name ai-messaging-ecs
```

**What this creates:**
- ECS Fargate cluster
- Task definitions for backend and frontend
- ECS services with auto-scaling
- Application Load Balancer
- Target groups and health checks

---

## 🔧 **Phase 3: Application Configuration (Week 3)**

### **Step 3.1: Database Migration**
```bash
# Get database endpoint
DB_ENDPOINT=$(aws rds describe-db-instances --query 'DBInstances[0].Endpoint.Address' --output text)

# Create migration script
cat > migrate_database.py << 'EOF'
import psycopg2
import os
from database.database_manager import DatabaseManager

# Database connection
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME', 'ai_messaging')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Connect and create tables
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# Run your existing database schema
# (Copy from your current database/schema.sql)
EOF

# Run migration
python migrate_database.py
```

### **Step 3.2: Environment Variables Setup**
```bash
# Create environment configuration
cat > backend.env << 'EOF'
# Database
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_NAME=ai_messaging
DB_USER=postgres
DB_PASSWORD=your-secure-password

# Redis
REDIS_HOST=your-elasticache-endpoint.cache.amazonaws.com
REDIS_PORT=6379

# S3
S3_BUCKET=ai-messaging-uploads
S3_REGION=us-east-1

# AI Services
GEMINI_API_KEY=your-gemini-api-key

# Application
NODE_ENV=production
PORT=8000
EOF
```

### **Step 3.3: Secrets Manager Setup**
```bash
# Store sensitive data in Secrets Manager
aws secretsmanager create-secret \
  --name "ai-messaging/database" \
  --description "Database credentials for AI Messaging Tool" \
  --secret-string '{"username":"postgres","password":"your-secure-password","host":"your-rds-endpoint"}'

aws secretsmanager create-secret \
  --name "ai-messaging/redis" \
  --description "Redis credentials for AI Messaging Tool" \
  --secret-string '{"host":"your-elasticache-endpoint","port":"6379"}'

aws secretsmanager create-secret \
  --name "ai-messaging/gemini" \
  --description "Gemini API key for AI Messaging Tool" \
  --secret-string '{"api_key":"your-gemini-api-key"}'
```

---

## 🌐 **Phase 4: API and Frontend Deployment (Week 4)**

### **Step 4.1: Create API Gateway**
```bash
# Create API Gateway CloudFormation stack
aws cloudformation create-stack \
  --stack-name ai-messaging-api \
  --template-body file://cloudformation/api-gateway.yaml \
  --parameters \
    ParameterKey=ECSStackName,ParameterValue=ai-messaging-ecs \
  --capabilities CAPABILITY_IAM

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name ai-messaging-api
```

**What this creates:**
- API Gateway REST API
- Lambda functions for file upload triggers
- SQS queues for message processing
- Integration with ECS services

### **Step 4.2: Deploy Frontend to S3 + CloudFront**
```bash
# Create CloudFront CloudFormation stack
aws cloudformation create-stack \
  --stack-name ai-messaging-cdn \
  --template-body file://cloudformation/cloudfront.yaml \
  --parameters \
    ParameterKey=StorageStackName,ParameterValue=ai-messaging-storage \
  --capabilities CAPABILITY_IAM

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name ai-messaging-cdn

# Build and deploy frontend
cd Automated-AI-Messaging-Tool-Frontend
npm run build
aws s3 sync out/ s3://ai-messaging-frontend-bucket --delete
```

### **Step 4.3: Configure Custom Domain (Optional)**
```bash
# Create Route 53 hosted zone
aws route53 create-hosted-zone \
  --name "yourdomain.com" \
  --caller-reference "ai-messaging-$(date +%s)"

# Create SSL certificate
aws acm request-certificate \
  --domain-name "yourdomain.com" \
  --validation-method DNS
```

---

## 📊 **Phase 5: Monitoring and Optimization (Week 5)**

### **Step 5.1: Setup CloudWatch Monitoring**
```bash
# Create monitoring CloudFormation stack
aws cloudformation create-stack \
  --stack-name ai-messaging-monitoring \
  --template-body file://cloudformation/monitoring.yaml \
  --parameters \
    ParameterKey=ECSStackName,ParameterValue=ai-messaging-ecs \
    ParameterKey=DatabaseStackName,ParameterValue=ai-messaging-database \
  --capabilities CAPABILITY_IAM

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name ai-messaging-monitoring
```

**What this creates:**
- CloudWatch dashboards
- Custom metrics and alarms
- X-Ray tracing configuration
- Log groups and log streams

### **Step 5.2: Setup Auto Scaling**
```bash
# Update ECS services with auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/ai-messaging-cluster/ai-messaging-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/ai-messaging-cluster/ai-messaging-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name ai-messaging-backend-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

---

## 🔄 **Phase 6: Data Migration and Testing (Week 6)**

### **Step 6.1: Migrate Data from Current Server**
```bash
# Create data migration script
cat > migrate_data.py << 'EOF'
import psycopg2
import boto3
import os
from datetime import datetime

# Source database (current server)
SOURCE_DB = {
    'host': '103.215.159.51',
    'database': 'ai_messaging',
    'user': 'postgres',
    'password': 'your-current-password'
}

# Target database (AWS RDS)
TARGET_DB = {
    'host': os.getenv('AWS_RDS_ENDPOINT'),
    'database': 'ai_messaging',
    'user': 'postgres',
    'password': os.getenv('AWS_RDS_PASSWORD')
}

# S3 client
s3 = boto3.client('s3')

def migrate_database():
    # Connect to both databases
    source_conn = psycopg2.connect(**SOURCE_DB)
    target_conn = psycopg2.connect(**TARGET_DB)
    
    # Migrate tables
    tables = ['users', 'file_uploads', 'websites', 'messages']
    
    for table in tables:
        print(f"Migrating {table}...")
        # Copy data from source to target
        # (Implementation details depend on your schema)
    
    source_conn.close()
    target_conn.close()

def migrate_files():
    # Migrate uploaded files to S3
    local_uploads_dir = '/path/to/current/uploads'
    s3_bucket = 'ai-messaging-uploads'
    
    for root, dirs, files in os.walk(local_uploads_dir):
        for file in files:
            local_path = os.path.join(root, file)
            s3_key = os.path.relpath(local_path, local_uploads_dir)
            
            s3.upload_file(local_path, s3_bucket, s3_key)
            print(f"Uploaded {s3_key}")

if __name__ == "__main__":
    migrate_database()
    migrate_files()
    print("Migration completed!")
EOF

# Run migration
python migrate_data.py
```

### **Step 6.2: Load Testing**
```bash
# Create load test script
cat > load_test.py << 'EOF'
import requests
import concurrent.futures
import time

API_BASE = "https://your-api-gateway-url.amazonaws.com"

def test_upload():
    # Test file upload endpoint
    files = {'file': open('test_file.csv', 'rb')}
    response = requests.post(f"{API_BASE}/upload", files=files)
    return response.status_code

def test_scraping():
    # Test website scraping endpoint
    data = {'urls': ['https://example.com']}
    response = requests.post(f"{API_BASE}/scrape", json=data)
    return response.status_code

def run_load_test():
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        
        # Submit 100 concurrent requests
        for _ in range(100):
            futures.append(executor.submit(test_upload))
            futures.append(executor.submit(test_scraping))
        
        # Wait for completion
        results = [future.result() for future in futures]
        
        success_rate = sum(1 for r in results if r == 200) / len(results)
        print(f"Success rate: {success_rate:.2%}")

if __name__ == "__main__":
    run_load_test()
EOF

# Run load test
python load_test.py
```

---

## 🎯 **Phase 7: Go Live and Optimization (Week 7)**

### **Step 7.1: DNS Cutover**
```bash
# Update DNS records to point to CloudFront
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890 \
  --change-batch file://dns-change.json
```

### **Step 7.2: Final Monitoring Setup**
```bash
# Create comprehensive monitoring dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "AI-Messaging-Tool-Production" \
  --dashboard-body file://monitoring-dashboard.json
```

### **Step 7.3: Cost Optimization**
```bash
# Setup cost alerts
aws budgets create-budget \
  --account-id 957440525184 \
  --budget file://cost-budget.json

# Enable cost anomaly detection
aws ce create-anomaly-monitor \
  --anomaly-monitor file://anomaly-monitor.json
```

---

## 📋 **CloudFormation Templates Required**

### **Template Files to Create:**
1. `cloudformation/vpc.yaml` - VPC and networking
2. `cloudformation/rds.yaml` - Database setup
3. `cloudformation/elasticache.yaml` - Redis cache
4. `cloudformation/s3.yaml` - Storage buckets
5. `cloudformation/ecr.yaml` - Container registry
6. `cloudformation/ecs.yaml` - ECS cluster and services
7. `cloudformation/api-gateway.yaml` - API management
8. `cloudformation/cloudfront.yaml` - CDN setup
9. `cloudformation/monitoring.yaml` - Monitoring and logging

---

## ⚠️ **Important Notes**

### **Pre-Migration Checklist:**
- [ ] Backup current database
- [ ] Document current environment variables
- [ ] Test application locally with new environment
- [ ] Prepare rollback plan
- [ ] Notify users of maintenance window

### **Post-Migration Checklist:**
- [ ] Verify all services are running
- [ ] Test all application features
- [ ] Monitor performance metrics
- [ ] Update DNS records
- [ ] Decommission old server

### **Estimated Timeline:**
- **Total Duration**: 7 weeks
- **Downtime**: 2-4 hours during DNS cutover
- **Cost**: $200-400/month (as per CSV estimates)

---

## 🚀 **Quick Start Commands**

```bash
# 1. Clone this repository and navigate to it
cd /Users/apple/Documents/aimsg

# 2. Create all CloudFormation templates (I'll help you create these)
# 3. Start with Phase 1
aws cloudformation create-stack --stack-name ai-messaging-vpc --template-body file://cloudformation/vpc.yaml --capabilities CAPABILITY_IAM

# 4. Monitor progress
aws cloudformation describe-stacks --stack-name ai-messaging-vpc --query 'Stacks[0].StackStatus'
```

---

*This migration plan provides a complete roadmap for moving your AI Messaging Tool to AWS with minimal downtime and maximum scalability.*
