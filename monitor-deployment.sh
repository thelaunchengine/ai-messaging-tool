#!/bin/bash

echo "🚀 AI Messaging Tool Deployment Monitor"
echo "======================================"
echo ""

# Function to check deployment status
check_deployment() {
    echo "📊 Current Deployment Status:"
    echo "-----------------------------"
    
    # Get current runs
    gh run list --limit 5 --json status,conclusion,workflowName,createdAt,url,number | jq -r '.[] | "\(.workflowName) #\(.number): \(.status) (\(.conclusion // "in_progress")) - \(.createdAt)"'
    
    echo ""
    echo "🔍 Detailed Status:"
    echo "------------------"
    
    # Check frontend deployment
    echo "Frontend Deployment:"
    gh run list --workflow="deploy-frontend.yml" --limit 1 --json status,conclusion,createdAt | jq -r '.[] | "  Status: \(.status) (\(.conclusion // "running")) - Started: \(.createdAt)"'
    
    # Check backend deployment  
    echo "Backend Deployment:"
    gh run list --workflow="deploy-backend.yml" --limit 1 --json status,conclusion,createdAt | jq -r '.[] | "  Status: \(.status) (\(.conclusion // "running")) - Started: \(.createdAt)"'
    
    echo ""
    echo "🌐 Application URLs:"
    echo "-------------------"
    echo "Frontend: http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:3000"
    echo "Backend:  http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8000"
    echo ""
}

# Function to test application endpoints
test_endpoints() {
    echo "🧪 Testing Application Endpoints:"
    echo "--------------------------------"
    
    echo "Testing Frontend..."
    FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:3000/ || echo "000")
    if [ "$FRONTEND_STATUS" = "200" ]; then
        echo "  ✅ Frontend: OK (HTTP $FRONTEND_STATUS)"
    else
        echo "  ❌ Frontend: Not ready (HTTP $FRONTEND_STATUS)"
    fi
    
    echo "Testing Backend..."
    BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8000/ || echo "000")
    if [ "$BACKEND_STATUS" = "200" ]; then
        echo "  ✅ Backend: OK (HTTP $BACKEND_STATUS)"
    else
        echo "  ❌ Backend: Not ready (HTTP $BACKEND_STATUS)"
    fi
    
    echo ""
}

# Main monitoring loop
while true; do
    clear
    check_deployment
    test_endpoints
    
    echo "⏰ Last updated: $(date)"
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    sleep 30
done
