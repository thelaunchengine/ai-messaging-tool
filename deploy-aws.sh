#!/bin/bash

# AWS CloudFormation Deployment Script for AI Messaging Tool
# This script deploys all CloudFormation stacks in the correct order

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
REGION=${2:-us-east-1}
STACK_PREFIX="ai-messaging"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is configured
check_aws_cli() {
    print_status "Checking AWS CLI configuration..."
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        print_error "AWS CLI is not configured or credentials are invalid"
        print_status "Please run: aws configure"
        exit 1
    fi
    print_success "AWS CLI is configured"
}

# Function to check if stack exists
stack_exists() {
    local stack_name=$1
    aws cloudformation describe-stacks --stack-name "$stack_name" --region "$REGION" > /dev/null 2>&1
}

# Function to wait for stack completion
wait_for_stack() {
    local stack_name=$1
    local operation=$2
    
    print_status "Waiting for $operation of $stack_name to complete..."
    aws cloudformation wait "stack-${operation}-complete" --stack-name "$stack_name" --region "$REGION"
    print_success "$operation of $stack_name completed"
}

# Function to deploy a single stack
deploy_stack() {
    local stack_name=$1
    local template_file=$2
    local parameters=$3
    
    print_status "Deploying $stack_name..."
    
    if stack_exists "$stack_name"; then
        print_warning "Stack $stack_name already exists, updating..."
        aws cloudformation update-stack \
            --stack-name "$stack_name" \
            --template-body "file://$template_file" \
            --parameters "$parameters" \
            --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
            --region "$REGION"
        wait_for_stack "$stack_name" "update"
    else
        print_status "Creating new stack $stack_name..."
        aws cloudformation create-stack \
            --stack-name "$stack_name" \
            --template-body "file://$template_file" \
            --parameters "$parameters" \
            --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
            --region "$REGION"
        wait_for_stack "$stack_name" "create"
    fi
    
    print_success "$stack_name deployed successfully"
}

# Function to get stack outputs
get_stack_output() {
    local stack_name=$1
    local output_key=$2
    aws cloudformation describe-stacks \
        --stack-name "$stack_name" \
        --region "$REGION" \
        --query "Stacks[0].Outputs[?OutputKey=='$output_key'].OutputValue" \
        --output text
}

# Main deployment function
main() {
    print_status "Starting AWS deployment for AI Messaging Tool"
    print_status "Environment: $ENVIRONMENT"
    print_status "Region: $REGION"
    print_status "Stack Prefix: $STACK_PREFIX"
    
    # Check prerequisites
    check_aws_cli
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Check if CloudFormation templates exist
    if [ ! -d "cloudformation" ]; then
        print_error "CloudFormation templates directory not found"
        exit 1
    fi
    
    print_status "Deploying CloudFormation stacks in order..."
    
    # Phase 1: Core Infrastructure
    print_status "=== Phase 1: Core Infrastructure ==="
    
    # 1. VPC and Networking
    deploy_stack "${STACK_PREFIX}-vpc" "cloudformation/vpc.yaml" "ParameterKey=Environment,ParameterValue=$ENVIRONMENT"
    
    # 2. Database
    print_status "Getting VPC stack outputs for database deployment..."
    VPC_STACK_NAME=$(get_stack_output "${STACK_PREFIX}-vpc" "VPCId" | cut -d'-' -f1-3)
    
    deploy_stack "${STACK_PREFIX}-database" "cloudformation/rds.yaml" \
        "ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
         ParameterKey=VPCStackName,ParameterValue=${STACK_PREFIX}-vpc \
         ParameterKey=DBPassword,ParameterValue=$(openssl rand -base64 32)"
    
    # 3. Cache
    deploy_stack "${STACK_PREFIX}-cache" "cloudformation/elasticache.yaml" \
        "ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
         ParameterKey=VPCStackName,ParameterValue=${STACK_PREFIX}-vpc"
    
    # 4. Storage
    deploy_stack "${STACK_PREFIX}-storage" "cloudformation/s3.yaml" \
        "ParameterKey=Environment,ParameterValue=$ENVIRONMENT"
    
    # Phase 2: Container Infrastructure
    print_status "=== Phase 2: Container Infrastructure ==="
    
    # 5. ECR
    deploy_stack "${STACK_PREFIX}-ecr" "cloudformation/ecr.yaml" \
        "ParameterKey=Environment,ParameterValue=$ENVIRONMENT"
    
    # 6. ECS
    deploy_stack "${STACK_PREFIX}-ecs" "cloudformation/ecs.yaml" \
        "ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
         ParameterKey=VPCStackName,ParameterValue=${STACK_PREFIX}-vpc \
         ParameterKey=DatabaseStackName,ParameterValue=${STACK_PREFIX}-database \
         ParameterKey=CacheStackName,ParameterValue=${STACK_PREFIX}-cache \
         ParameterKey=StorageStackName,ParameterValue=${STACK_PREFIX}-storage \
         ParameterKey=ECRStackName,ParameterValue=${STACK_PREFIX}-ecr"
    
    # Phase 3: API and CDN
    print_status "=== Phase 3: API and CDN ==="
    
    # 7. API Gateway
    deploy_stack "${STACK_PREFIX}-api" "cloudformation/api-gateway.yaml" \
        "ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
         ParameterKey=ECSStackName,ParameterValue=${STACK_PREFIX}-ecs \
         ParameterKey=StorageStackName,ParameterValue=${STACK_PREFIX}-storage"
    
    # 8. CloudFront
    deploy_stack "${STACK_PREFIX}-cdn" "cloudformation/cloudfront.yaml" \
        "ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
         ParameterKey=StorageStackName,ParameterValue=${STACK_PREFIX}-storage"
    
    # Phase 4: Monitoring
    print_status "=== Phase 4: Monitoring ==="
    
    # 9. Monitoring
    deploy_stack "${STACK_PREFIX}-monitoring" "cloudformation/monitoring.yaml" \
        "ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
         ParameterKey=ECSStackName,ParameterValue=${STACK_PREFIX}-ecs \
         ParameterKey=DatabaseStackName,ParameterValue=${STACK_PREFIX}-database \
         ParameterKey=CacheStackName,ParameterValue=${STACK_PREFIX}-cache \
         ParameterKey=APIGatewayStackName,ParameterValue=${STACK_PREFIX}-api \
         ParameterKey=CloudFrontStackName,ParameterValue=${STACK_PREFIX}-cdn"
    
    # Get final outputs
    print_status "=== Deployment Complete ==="
    print_success "All CloudFormation stacks deployed successfully!"
    
    # Display important outputs
    print_status "Getting deployment outputs..."
    
    ALB_DNS=$(get_stack_output "${STACK_PREFIX}-ecs" "ApplicationLoadBalancerDNS")
    CLOUDFRONT_URL=$(get_stack_output "${STACK_PREFIX}-cdn" "CloudFrontURL")
    API_GATEWAY_URL=$(get_stack_output "${STACK_PREFIX}-api" "APIGatewayURL")
    
    echo ""
    print_success "=== Deployment Summary ==="
    echo "Environment: $ENVIRONMENT"
    echo "Region: $REGION"
    echo "Application Load Balancer: http://$ALB_DNS"
    echo "CloudFront URL: $CLOUDFRONT_URL"
    echo "API Gateway URL: $API_GATEWAY_URL"
    echo ""
    print_status "Next steps:"
    echo "1. Build and push Docker images to ECR"
    echo "2. Update ECS services with new image tags"
    echo "3. Configure custom domain (optional)"
    echo "4. Set up monitoring alerts"
    echo ""
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@"

