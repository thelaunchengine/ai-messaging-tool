# CloudFormation Templates for AI Messaging Tool

This directory contains CloudFormation templates for deploying the AI Messaging Tool to AWS.

## 📋 **Template Overview**

| Template | Description | Dependencies |
|----------|-------------|--------------|
| `vpc.yaml` | VPC, subnets, security groups, NAT gateways | None |
| `rds.yaml` | PostgreSQL database with Multi-AZ | VPC |
| `elasticache.yaml` | Redis cache cluster | VPC |
| `s3.yaml` | S3 buckets for file storage and frontend | None |
| `ecr.yaml` | ECR repositories for container images | None |
| `ecs.yaml` | ECS Fargate cluster and services | VPC, RDS, Cache, S3, ECR |
| `api-gateway.yaml` | API Gateway with Lambda functions | ECS, S3 |
| `cloudfront.yaml` | CloudFront CDN for frontend | S3 |
| `monitoring.yaml` | CloudWatch monitoring and alarms | All stacks |

## 🚀 **Quick Start**

### **Option 1: Automated Deployment**
```bash
# Deploy all stacks automatically
./deploy-aws.sh production us-east-1

# Deploy to different environment
./deploy-aws.sh development us-west-2
```

### **Option 2: Manual Deployment**
```bash
# 1. Deploy VPC
aws cloudformation create-stack \
  --stack-name ai-messaging-vpc \
  --template-body file://cloudformation/vpc.yaml \
  --capabilities CAPABILITY_IAM

# 2. Deploy Database
aws cloudformation create-stack \
  --stack-name ai-messaging-database \
  --template-body file://cloudformation/rds.yaml \
  --parameters ParameterKey=VPCStackName,ParameterValue=ai-messaging-vpc \
  --capabilities CAPABILITY_IAM

# 3. Continue with other stacks...
```

## 📊 **Deployment Phases**

### **Phase 1: Core Infrastructure (Week 1)**
- **VPC**: Network isolation and security
- **RDS**: PostgreSQL database with Multi-AZ
- **ElastiCache**: Redis cache cluster
- **S3**: File storage buckets

### **Phase 2: Container Infrastructure (Week 2)**
- **ECR**: Container image repositories
- **ECS**: Fargate cluster and services
- **Load Balancer**: Application load balancer

### **Phase 3: API and CDN (Week 3)**
- **API Gateway**: REST API management
- **CloudFront**: Global CDN for frontend
- **Lambda**: Event processing functions

### **Phase 4: Monitoring (Week 4)**
- **CloudWatch**: Monitoring and logging
- **Alarms**: Automated alerting
- **Dashboard**: Centralized monitoring

## 🔧 **Configuration Parameters**

### **Environment Parameters**
- `Environment`: development, staging, production
- `Region`: AWS region (default: us-east-1)
- `VPCStackName`: Name of VPC stack
- `DatabaseStackName`: Name of database stack
- `CacheStackName`: Name of cache stack
- `StorageStackName`: Name of storage stack
- `ECSStackName`: Name of ECS stack
- `ECRStackName`: Name of ECR stack

### **Resource Parameters**
- `DBInstanceClass`: Database instance type
- `NodeType`: Cache node type
- `BackendCpu`: Backend container CPU
- `BackendMemory`: Backend container memory
- `DesiredCount`: Number of ECS tasks
- `MaxCount`: Maximum number of tasks
- `MinCount`: Minimum number of tasks

## 💰 **Cost Estimation**

| Service | Development | Production |
|---------|-------------|------------|
| VPC | $0 | $0 |
| RDS (db.t3.small) | $30/month | $60/month |
| ElastiCache (cache.t3.micro) | $19/month | $38/month |
| S3 | $2/month | $5/month |
| ECS Fargate | $58/month | $120/month |
| ECR | $0.10/month | $0.20/month |
| API Gateway | $0.35/month | $3.50/month |
| CloudFront | $8.50/month | $17/month |
| CloudWatch | $10/month | $20/month |
| **Total** | **$127.95/month** | **$263.70/month** |

## 🔐 **Security Features**

### **Network Security**
- VPC with public/private subnets
- Security groups with least privilege
- NAT gateways for outbound traffic
- No direct internet access to private resources

### **Data Security**
- Encryption at rest for all storage
- Encryption in transit for all communications
- Secrets Manager for sensitive data
- IAM roles with minimal permissions

### **Application Security**
- WAF for web application protection
- CloudFront for DDoS protection
- API Gateway for rate limiting
- CloudWatch for security monitoring

## 📈 **Scaling Features**

### **Auto Scaling**
- ECS services with auto scaling
- CPU and memory-based scaling
- Scheduled scaling for predictable loads
- Spot instances for cost optimization

### **Load Balancing**
- Application Load Balancer
- Health checks and failover
- SSL termination
- Path-based routing

### **Caching**
- CloudFront for global caching
- ElastiCache for application caching
- S3 for static asset caching
- API Gateway response caching

## 🔍 **Monitoring Features**

### **CloudWatch Metrics**
- ECS service metrics
- RDS database metrics
- ElastiCache metrics
- API Gateway metrics
- CloudFront metrics

### **Alarms**
- High CPU utilization
- High memory utilization
- High error rates
- Low disk space
- High latency

### **Logging**
- Centralized logging with CloudWatch
- Log retention policies
- Log aggregation and analysis
- Custom log groups

## 🛠 **Maintenance**

### **Updates**
- Rolling updates for ECS services
- Blue/green deployments
- Database maintenance windows
- Cache cluster updates

### **Backups**
- Automated RDS backups
- S3 versioning and lifecycle
- Cross-region replication
- Point-in-time recovery

### **Monitoring**
- Health checks and alerts
- Performance monitoring
- Cost monitoring
- Security monitoring

## 🚨 **Troubleshooting**

### **Common Issues**
1. **Stack creation fails**: Check IAM permissions
2. **ECS tasks not starting**: Check security groups
3. **Database connection fails**: Check VPC configuration
4. **CloudFront not working**: Check S3 bucket policy

### **Debug Commands**
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name ai-messaging-vpc

# Check ECS service status
aws ecs describe-services --cluster ai-messaging-cluster --services ai-messaging-backend-service

# Check RDS status
aws rds describe-db-instances --db-instance-identifier ai-messaging-db

# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix /aws/ecs
```

## 📚 **Additional Resources**

- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [ECS Fargate Documentation](https://docs.aws.amazon.com/ecs/latest/developerguide/AWS_Fargate.html)
- [RDS PostgreSQL Documentation](https://docs.aws.amazon.com/rds/latest/userguide/CHAP_PostgreSQL.html)
- [ElastiCache Redis Documentation](https://docs.aws.amazon.com/elasticache/latest/red-ug/)

## 🤝 **Support**

For issues or questions:
1. Check the troubleshooting section
2. Review CloudFormation stack events
3. Check CloudWatch logs
4. Contact the development team

---

*This infrastructure supports processing 500,000+ records efficiently with automatic scaling, high availability, and enterprise-grade security.*

