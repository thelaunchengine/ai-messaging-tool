# 🚀 Celery Fixes Deployment Instructions

## 📦 What's Fixed
- ✅ **AsyncResult serialization errors** - Tasks now return serializable data
- ✅ **Circular import issues** - Using `celery_app.send_task()` instead of direct imports
- ✅ **Syntax errors** - Fixed malformed try/except blocks
- ✅ **Error handling** - Comprehensive error recovery and logging

## 📁 Files to Deploy
- `celery_tasks/file_tasks.py` - Fixed AsyncResult serialization
- `celery_tasks/scraping_tasks.py` - Fixed circular imports and error handling
- `celery_tasks/form_submission_tasks.py` - Fixed syntax errors

## 🔧 Deployment Steps

### Step 1: Upload Fixed Files
```bash
# Upload the fixed celery_tasks directory
scp -i [your-ssh-key] -r /Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Backend/celery_tasks/ ec2-user@98.85.16.204:/var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend/
```

### Step 2: SSH into EC2 and Restart Services
```bash
# Connect to EC2
ssh -i [your-ssh-key] ec2-user@98.85.16.204

# Navigate to backend directory
cd /var/www/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend/

# Restart Celery workers
sudo systemctl restart celery-worker
sudo systemctl restart celery-beat

# Restart the backend API
sudo systemctl restart ai-messaging-backend

# Check service status
sudo systemctl status celery-worker
sudo systemctl status ai-messaging-backend
```

### Step 3: Test the Fixes
```bash
# Test upload endpoint
curl -X POST "http://98.85.16.204:8001/api/upload-from-frontend?userId=test-user-123" \
  -F "file=@test.csv" \
  -H "Content-Type: multipart/form-data"

# Check task status (replace with actual task ID)
curl "http://98.85.16.204:8001/api/task-status/[TASK_ID]"
```

## ✅ Expected Results
- **Before**: `"TypeError('Object of type AsyncResult is not JSON serializable')"`
- **After**: Tasks complete successfully with proper status updates

## 🔍 Verification
The fixed tasks should now:
1. ✅ Process file uploads without serialization errors
2. ✅ Automatically trigger scraping tasks
3. ✅ Automatically trigger AI message generation
4. ✅ Automatically trigger contact form submission
5. ✅ Update database with proper status information

## 📞 Support
If you encounter any issues during deployment, the local test script `test_celery_fixes.py` can be used to verify the fixes are working correctly.
