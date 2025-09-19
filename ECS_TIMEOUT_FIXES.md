# ECS Operation Timeout Fixes

## Issues Identified and Fixed

### 1. **Health Check Port Mismatch** ✅ FIXED
- **Problem**: ECS health check was hitting port `8000` but app runs on port `8001`
- **Solution**: Updated health check to use correct port and endpoint
- **Changes**:
  - Health check URL: `http://localhost:8001/api/health`
  - Container port mapping: `8001`
  - Load balancer port: `8001`
  - Environment variable: `PORT=8001`

### 2. **Health Check Timeout Settings** ✅ FIXED
- **Problem**: Insufficient timeout and retry settings
- **Solution**: Increased timeout values for better reliability
- **Changes**:
  - Timeout: `5s` → `10s`
  - Retries: `3` → `5`
  - Start Period: `60s` → `120s`
  - Interval: `30s` (unchanged)

### 3. **Long-Running Operations** ✅ FIXED
- **Problem**: No timeout handling for async operations
- **Solution**: Added comprehensive timeout handling
- **Changes**:
  - File upload: 5-minute timeout with `asyncio.wait_for()`
  - AI generation: 2 minutes per website, max 10 minutes total
  - FastAPI app: 5-minute default timeout
  - Uvicorn: 5-minute keep-alive timeout

### 4. **Resource Allocation** ✅ FIXED
- **Problem**: Insufficient CPU/memory for production workload
- **Solution**: Increased resource allocation
- **Changes**:
  - Backend CPU: `512` → `1024` units
  - Backend Memory: `1024` → `2048` MB
  - Worker CPU: `1024` → `2048` units
  - Worker Memory: `2048` → `4096` MB

### 5. **Environment Variables** ✅ FIXED
- **Problem**: Missing timeout configuration
- **Solution**: Added timeout environment variables
- **Added**:
  - `TIMEOUT_PER_WEBSITE=300`
  - `TIMEOUT_PER_BATCH=900`
  - `TIMEOUT_PER_CHUNK=600`
  - `QUEUE_TIMEOUT=300`
  - `DB_POOL_TIMEOUT=30`

## Deployment Instructions

### 1. Update ECS Task Definition
```bash
# Deploy the updated CloudFormation template
aws cloudformation update-stack \
  --stack-name production-ai-messaging-ecs \
  --template-body file://cloudformation/ecs-services-fixed.yaml \
  --parameters ParameterKey=Environment,ParameterValue=production \
  --region us-east-1
```

### 2. Force New Deployment
```bash
# Force ECS service to use new task definition
aws ecs update-service \
  --cluster production-ai-messaging-cluster \
  --service production-ai-messaging-backend-service \
  --force-new-deployment \
  --region us-east-1
```

### 3. Monitor Deployment
```bash
# Check service status
aws ecs describe-services \
  --cluster production-ai-messaging-cluster \
  --services production-ai-messaging-backend-service \
  --region us-east-1

# Check task health
aws ecs list-tasks \
  --cluster production-ai-messaging-cluster \
  --service-name production-ai-messaging-backend-service \
  --region us-east-1
```

## Expected Improvements

1. **Health Check Reliability**: Better success rate with correct port and increased timeouts
2. **Operation Stability**: Long-running operations won't cause ECS timeouts
3. **Performance**: Increased resources should handle higher loads
4. **Monitoring**: Better timeout handling with proper error messages

## Monitoring Commands

```bash
# Test health endpoint
curl http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001/api/health

# Check ECS service logs
aws logs tail /aws/ecs/production-ai-messaging-backend --follow --region us-east-1

# Monitor task metrics
aws ecs describe-tasks \
  --cluster production-ai-messaging-cluster \
  --tasks $(aws ecs list-tasks --cluster production-ai-messaging-cluster --service-name production-ai-messaging-backend-service --query 'taskArns[0]' --output text) \
  --region us-east-1
```

## Files Modified

1. `cloudformation/ecs-services-fixed.yaml` - ECS task definition updates
2. `Automated-AI-Messaging-Tool-Backend/main.py` - Timeout handling and uvicorn config

## Next Steps

1. Deploy the updated configuration
2. Monitor ECS service health and performance
3. Test long-running operations (file uploads, AI generation)
4. Adjust resource allocation if needed based on actual usage
