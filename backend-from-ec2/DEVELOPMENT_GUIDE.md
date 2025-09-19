# 🚀 AI Messaging Project - Development Guide

## 📋 **Project Overview**

This is a **full-stack AI messaging application** with two separate codebases that work together:

### **Backend (Python/FastAPI)**
- **Location**: `/Users/apple/Downloads/ai-messaging-python-backend/`
- **Technology**: Python, FastAPI, Celery, PostgreSQL, Redis
- **Purpose**: API server, background tasks, database management
- **Port**: 8000
- **Server**: `103.215.159.51:8000`

### **Frontend (Next.js)**
- **Location**: `/Users/apple/Downloads/aimsg_onserver/Automated-AI-Messaging-Tool-Frontend/`
- **Technology**: Next.js, React, TypeScript, Material-UI
- **Purpose**: Admin interface, user management, file uploads
- **Port**: 3001
- **Server**: `103.215.159.51:3001`

## 🔄 **Development Workflow**

### **Backend Development**
```bash
# Start automatic file watching
cd /Users/apple/Downloads/ai-messaging-python-backend/
./watch-and-upload.sh

# Manual upload
./upload-to-server.sh

# Check health
curl http://103.215.159.51:8000/health
```

### **Frontend Development**
```bash
# Start local development
cd /Users/apple/Downloads/aimsg_onserver/Automated-AI-Messaging-Tool-Frontend/
npm run dev

# Build for production
npm run build
```

## 🔗 **Integration Points**

### **API Communication**
- Frontend calls backend APIs for data operations
- Backend provides RESTful endpoints
- Shared data models and schemas

### **File Uploads**
- Frontend uploads files to backend
- Backend processes files with Celery tasks
- Real-time status updates via API

### **Database**
- Backend manages PostgreSQL database
- Frontend displays data from backend APIs
- Shared data models

## 📁 **Key Files Structure**

### **Backend Key Files**
```
ai-messaging-python-backend/
├── main.py                 # FastAPI app
├── celery_app.py          # Celery configuration
├── celery_tasks/          # Background tasks
│   ├── file_tasks.py
│   ├── scraping_tasks.py
│   └── form_submission_tasks.py
├── database/              # Database models
│   ├── database_manager.py
│   └── models.py
├── ai/                    # AI message generation
│   └── message_generator.py
├── scraping/              # Web scraping
│   └── scraper.py
├── upload-to-server.sh    # Manual upload
├── watch-and-upload.sh    # Automatic upload
└── requirements.txt       # Python dependencies
```

### **Frontend Key Files**
```
Automated-AI-Messaging-Tool-Frontend/
├── src/
│   ├── app/               # Next.js app router
│   │   ├── (dashboard)/   # Dashboard pages
│   │   │   ├── file-upload/
│   │   │   ├── history/
│   │   │   └── manual-workflow/
│   │   └── api/           # API routes
│   ├── components/        # React components
│   └── lib/              # Utilities
├── package.json          # Node.js dependencies
└── next.config.js       # Next.js configuration
```

## 🎯 **Development Considerations**

### **When Making Backend Changes**
1. **API Endpoints**: Update frontend API calls if needed
2. **Database Models**: Ensure frontend can handle new data structures
3. **Configuration**: Update environment variables for both codebases
4. **File Processing**: Test frontend upload functionality

### **When Making Frontend Changes**
1. **API Calls**: Ensure backend endpoints support the requests
2. **Data Display**: Verify backend provides required data
3. **UI Components**: Test with real backend data
4. **File Uploads**: Ensure backend can process uploaded files

### **Cross-Codebase Changes**
1. **New Features**: Implement in both backend and frontend
2. **Bug Fixes**: Check both codebases for related issues
3. **Performance**: Optimize both API calls and UI rendering
4. **Security**: Apply security measures to both codebases

## 🚀 **Deployment Workflow**

### **Backend Deployment**
- **Automatic**: File watcher uploads and restarts services
- **Manual**: Use upload scripts
- **Services**: FastAPI + Celery workers

### **Frontend Deployment**
- **Manual**: Build and deploy to server
- **Process**: `npm run build` → upload to server
- **Service**: Next.js application

## 📊 **Monitoring & Debugging**

### **Backend Monitoring**
```bash
# Check service status
ssh backend-server 'systemctl status ai-messaging-backend.service'
ssh backend-server 'systemctl status ai-messaging-celery.service'

# Check logs
ssh backend-server 'tail -f logs/celery.log'
ssh backend-server 'journalctl -u ai-messaging-backend.service -f'

# Health check
curl http://103.215.159.51:8000/health
```

### **Frontend Monitoring**
```bash
# Check if frontend is running
curl http://103.215.159.51:3001

# Check Next.js logs
ssh backend-server 'pm2 logs aimsg-frontend'
```

## 🔧 **Common Development Tasks**

### **Adding New API Endpoint**
1. **Backend**: Add endpoint in `main.py`
2. **Frontend**: Create API call in `src/app/api/`
3. **Test**: Verify data flow between both

### **Adding New Database Model**
1. **Backend**: Add model in `database/models.py`
2. **Frontend**: Update interfaces and API calls
3. **Migration**: Update database schema

### **Adding New UI Component**
1. **Frontend**: Create component in `src/components/`
2. **Backend**: Ensure API supports required data
3. **Integration**: Test with real backend data

## 🎉 **Best Practices**

1. **Always consider both codebases** when making changes
2. **Test API integration** between frontend and backend
3. **Use the upload system** for backend development
4. **Monitor both services** during development
5. **Keep configurations** synchronized between environments

---

**Remember: This is a full-stack application where both codebases work together! 🚀** 