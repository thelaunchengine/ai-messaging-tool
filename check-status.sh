#!/bin/bash

# Status check script for AI Messaging Tool deployment

echo "🔍 Checking deployment status..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check ECS cluster
echo -e "${YELLOW}ECS Cluster Status:${NC}"
aws ecs describe-clusters --clusters production-ai-messaging-cluster --query 'clusters[0].{Name:clusterName,Status:status,ActiveServices:activeServicesCount}' --output table

# Check ECS services
echo -e "\n${YELLOW}ECS Services Status:${NC}"
aws ecs describe-services --cluster production-ai-messaging-cluster --services production-ai-messaging-backend-service --query 'services[0].{Name:serviceName,Status:status,RunningCount:runningCount,DesiredCount:desiredCount}' --output table

# Check running tasks
echo -e "\n${YELLOW}Running Tasks:${NC}"
aws ecs list-tasks --cluster production-ai-messaging-cluster --query 'taskArns' --output table

# Check load balancer
echo -e "\n${YELLOW}Load Balancer Status:${NC}"
aws elbv2 describe-load-balancers --query 'LoadBalancers[?contains(LoadBalancerName, `ai-messaging`)].{Name:LoadBalancerName,DNS:DNSName,State:State.Code}' --output table

# Check target groups
echo -e "\n${YELLOW}Target Groups Health:${NC}"
aws elbv2 describe-target-groups --query 'TargetGroups[?contains(TargetGroupName, `backend`) || contains(TargetGroupName, `frontend`)].{Name:TargetGroupName,Port:Port,Protocol:Protocol}' --output table

# Get application URLs
ALB_DNS=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[?contains(LoadBalancerName, `ai-messaging`)].DNSName' --output text 2>/dev/null)

if [ ! -z "$ALB_DNS" ]; then
    echo -e "\n${GREEN}🚀 Application URLs:${NC}"
    echo "Frontend: http://$ALB_DNS:3000"
    echo "Backend: http://$ALB_DNS:8000"
    echo "Health Check: http://$ALB_DNS:8000/health"
    
    # Test health endpoint
    echo -e "\n${YELLOW}Testing health endpoint...${NC}"
    curl -s -o /dev/null -w "Health check status: %{http_code}\n" http://$ALB_DNS:8000/health || echo "Health check failed"
else
    echo -e "\n${RED}❌ Load balancer not found${NC}"
fi
