# AI Messaging Tool - Complete Deployment Guide

## 📋 **Project Overview**
- **Frontend**: Next.js 14.2.32 with NextAuth.js 4.24.7
- **Backend**: Python 3.11 with FastAPI and Celery
- **Authentication**: NextAuth.js with JWT strategy
- **Database**: SQLite with ChromaDB for AI embeddings
- **Process Manager**: Systemd services
- **Server**: Ubuntu/Linux with SSH access

### **📁 Project Paths**
- **Backend Local Path**: `/Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Backend`
- **Frontend Local Path**: `/Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Frontend`
- **Backend Remote Path**: `/home/xb3353/Automated-AI-Messaging-Tool-Backend`
- **Frontend Remote Path**: `/home/xb3353/Automated-AI-Messaging-Tool-Frontend`

### **🔐 SSH Connection Details**
- **Host**: `103.215.159.51`
- **Port**: `22`
- **Username**: `xb3353`
- **SSH Alias**: `backend-server` (configured for passwordless access)

---

## 🚀 **Backend Deployment (Python/FastAPI)**

### **1. Server Requirements**
- Ubuntu/Linux server with SSH access
- Python 3.11+ installed
- Virtual environment support
- Port 8000 available for backend
- Systemd service management

### **2. Backend Environment Variables**
Create `.env` file in backend root:
```env
# Database
DATABASE_URL="sqlite:///./chroma_db/chroma.sqlite3"

# JWT
JWT_SECRET="your-jwt-secret-key-here"
NEXTAUTH_SECRET="your-nextauth-secret-key-here"

# Server
PORT=8000
NODE_ENV=production

# CORS (Frontend URL)
FRONTEND_URL="http://103.215.159.51:3001"

# AI Configuration
OPENAI_API_KEY="your-openai-api-key"
GEMINI_API_KEY="your-gemini-api-key"
```

### **3. Backend Installation & Setup**
```bash
# Navigate to backend directory
cd /Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database/init_db.py

# Test the application
python app.py
```

### **4. Backend Systemd Service Configuration**
Create `ai-messaging-backend.service`:
```ini
[Unit]
Description=AI Messaging Backend FastAPI Server
After=network.target

[Service]
Type=simple
User=xb3353
Group=xb3353
WorkingDirectory=/home/xb3353/Automated-AI-Messaging-Tool-Backend
Environment=PATH=/home/xb3353/Automated-AI-Messaging-Tool-Backend/venv/bin
ExecStart=/home/xb3353/Automated-AI-Messaging-Tool-Backend/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **5. Celery Worker Service Configuration**
Create `ai-messaging-celery.service`:
```ini
[Unit]
Description=AI Messaging Celery Worker
After=network.target

[Service]
Type=simple
User=xb3353
Group=xb3353
WorkingDirectory=/home/xb3353/Automated-AI-Messaging-Tool-Backend
Environment=PATH=/home/xb3353/Automated-AI-Messaging-Tool-Backend/venv/bin
ExecStart=/home/xb3353/Automated-AI-Messaging-Tool-Backend/venv/bin/celery -A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname=worker@%h --max-tasks-per-child=1000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🎨 **Frontend Deployment (Next.js)**

### **1. Server Requirements**
- Same server as backend (or separate server)
- Node.js 18+ installed
- PM2 globally installed
- Port 3001 available for frontend
- Nginx (optional, for reverse proxy)

### **2. Frontend Environment Variables**
Create `.env.local` file in frontend root:
```env
# Backend API URL
NEXT_PUBLIC_BACKEND_URL="http://103.215.159.51:8000"

# NextAuth Configuration
NEXTAUTH_URL="http://103.215.159.51:3001"
NEXTAUTH_SECRET="your-nextauth-secret-key-here"

# Base URL
NEXT_PUBLIC_BASE_URL="http://103.215.159.51:3001"
```

### **3. Frontend Installation & Setup**
```bash
# Navigate to frontend directory
cd /Users/apple/Documents/aimsg/Automated-AI-Messaging-Tool-Frontend

# Install dependencies
npm install

# Build the application (optional for development)
npm run build

# Start with PM2 (ALWAYS use sudo)
sudo pm2 start ecosystem.config.js --name Frontend
```

**🚨 CRITICAL: ALWAYS use `sudo pm2` for all PM2 commands on the server!**

### **4. Frontend PM2 Configuration (DEVELOPMENT MODE)**
Create `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [{
    name: 'Frontend',
    script: 'npm',
    args: 'run dev',  // ✅ ALWAYS use 'run dev' for development mode
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    cwd: '/home/xb3353/Automated-AI-Messaging-Tool-Frontend',
    env: {
      NODE_ENV: 'development',  // ✅ ALWAYS use 'development' for development
      PORT: 3001,
      NEXT_PUBLIC_BACKEND_URL: 'http://103.215.159.51:8000',
      NEXTAUTH_URL: 'http://103.215.159.51:3001',
      NEXTAUTH_SECRET: 'your-nextauth-secret-key-here',
      NEXT_PUBLIC_BASE_URL: 'http://103.215.159.51:3001'
    }
  }]
};
```

**🚨 IMPORTANT: Frontend should ALWAYS run in development mode for faster development and debugging!**

---

## 🔄 **Automatic Upload System (Already Configured)**

### **1. SSH Key Authentication**
```bash
# SSH alias configured for passwordless access
ssh backend-server

# No password prompts during development
```

### **2. Backend Upload Scripts**
```bash
# Manual upload with service restart
./upload-to-server.sh

# Automatic file watching and uploading
./watch-and-upload.sh

# Test automatic upload
./test-automatic-upload.sh
```

### **3. VS Code Integration**
- 10 built-in tasks accessible via Command Palette
- Quick access to upload, health check, and monitoring tasks
- Press `Cmd/Ctrl + Shift + P` → "Tasks: Run Task"

---

## 🚀 **Frontend Upload Automation (New)**

### **1. Create Frontend Upload Script**
Create `upload-frontend-to-server.sh`:
```bash
#!/bin/bash

# Frontend Upload Script
# Automatically uploads frontend files and restarts services

set -e

# Configuration
REMOTE_HOST="backend-server"
REMOTE_FRONTEND_PATH="/home/xb3353/Automated-AI-Messaging-Tool-Frontend"
STAGING_DIR="toUpload"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Frontend Upload Script${NC}"

# Create staging directory if it doesn't exist
if [ ! -d "$STAGING_DIR" ]; then
    mkdir -p "$STAGING_DIR"
fi

# Copy frontend files to staging
echo -e "${YELLOW}📁 Copying frontend files to staging...${NC}"
rsync -av --exclude='node_modules' --exclude='.next' --exclude='.git' \
    --exclude='*.log' --exclude='*.tmp' --exclude='*.swp' \
    --exclude='__pycache__' --exclude='*.pyc' \
    ./ "$STAGING_DIR/"

# Upload to server
echo -e "${YELLOW}📤 Uploading to server...${NC}"
rsync -avz --delete "$STAGING_DIR/" "$REMOTE_HOST:$REMOTE_FRONTEND_PATH/"

# Restart frontend service
echo -e "${YELLOW}🔄 Restarting frontend service...${NC}"
ssh "$REMOTE_HOST" 'sudo pm2 restart Frontend'

# Clean up staging directory
echo -e "${YELLOW}🧹 Cleaning up staging directory...${NC}"
rm -rf "$STAGING_DIR"

echo -e "${GREEN}✅ Frontend upload complete!${NC}"
echo -e "${GREEN}🌐 Frontend available at: http://103.215.159.51:3001${NC}"
```

**🚨 IMPORTANT: Update the script to use `sudo pm2 restart Frontend` instead of `pm2 restart Frontend`**

---

## 🚨 **PM2 Management (CRITICAL RULES)**

### **1. PM2 Commands (ALWAYS with sudo)**
```bash
# ✅ CORRECT - Always use sudo for PM2 commands
sudo pm2 list                    # List all processes
sudo pm2 start Frontend          # Start frontend
sudo pm2 restart Frontend        # Restart frontend
sudo pm2 stop Frontend           # Stop frontend
sudo pm2 delete Frontend         # Delete frontend process
sudo pm2 show Frontend           # Show frontend details
sudo pm2 logs Frontend           # Show frontend logs
sudo pm2 monit                   # Monitor all processes
sudo pm2 save                    # Save PM2 configuration
sudo pm2 startup                 # Setup PM2 startup script

# ❌ WRONG - Never use without sudo
pm2 list
pm2 start Frontend
pm2 restart Frontend
```

### **2. Why sudo is Required**
- PM2 services need root privileges to run properly
- Without sudo, services may fail to start or have permission issues
- All PM2 commands must be prefixed with `sudo`

### **3. Frontend Development Mode**
- **ALWAYS use `npm run dev`** instead of `npm start`
- **NODE_ENV should be `development`** for faster development
- **Development mode enables**: Hot reloading, debugging, faster builds

### **2. Create Frontend File Watcher**
Create `watch-and-upload-frontend.sh`:
```bash
#!/bin/bash

# Frontend File Watcher
# Automatically uploads frontend files when they change

set -e

# Configuration
WATCH_DIRS=("src" "public" "components" "views" "themes" "utils" "types" "hooks" "lib" "config" "menu-items" "sections" "data")
EXCLUDE_PATTERNS=("node_modules" ".next" ".git" "*.log" "*.tmp" "*.swp" "__pycache__" "*.pyc")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}👀 Frontend File Watcher Started${NC}"
echo -e "${BLUE}Watching directories: ${WATCH_DIRS[*]}${NC}"
echo -e "${BLUE}Press Ctrl+C to stop${NC}"
echo ""

# Build exclude pattern for fswatch
EXCLUDE_ARGS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$pattern"
done

# Watch for changes and upload
fswatch -o $EXCLUDE_ARGS "${WATCH_DIRS[@]}" | while read f; do
    echo -e "${YELLOW}📝 Change detected! Uploading frontend...${NC}"
    ./upload-frontend-to-server.sh
    echo -e "${GREEN}✅ Upload complete!${NC}"
    echo ""
done
```

### **3. Make Scripts Executable**
```bash
chmod +x upload-frontend-to-server.sh
chmod +x watch-and-upload-frontend.sh
```

---

## 🔐 **Server Setup for Passwordless Service Management**

### **1. SSH into server**
```bash
ssh xb3353@103.215.159.51
```

### **2. Edit sudoers file**
```bash
sudo visudo
```

### **3. Add these lines at the end**
```
# AI Messaging Service Restart Permissions
xb3353 ALL=NOPASSWD: /bin/systemctl restart ai-messaging-backend.service
xb3353 ALL=NOPASSWD: /bin/systemctl status ai-messaging-backend.service
xb3353 ALL=NOPASSWD: /bin/systemctl restart ai-messaging-celery.service
xb3353 ALL=NOPASSWD: /bin/systemctl status ai-messaging-celery.service
xb3353 ALL=NOPASSWD: /bin/systemctl stop ai-messaging-backend.service
xb3353 ALL=NOPASSWD: /bin/systemctl start ai-messaging-backend.service
xb3353 ALL=NOPASSWD: /bin/systemctl stop ai-messaging-celery.service
xb3353 ALL=NOPASSWD: /bin/systemctl start ai-messaging-celery.service
xb3353 ALL=NOPASSWD: /usr/bin/pm2 restart Frontend
xb3353 ALL=NOPASSWD: /usr/bin/pm2 status Frontend
```

### **4. Enable and start services**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-messaging-backend.service
sudo systemctl enable ai-messaging-celery.service
sudo systemctl start ai-messaging-backend.service
sudo systemctl start ai-messaging-celery.service
```

---

## 🧪 **Testing the Setup**

### **1. Test Backend Health**
```bash
curl http://103.215.159.51:8000/health
```

### **2. Test Frontend Access**
```bash
curl http://103.215.159.51:3001
```

### **3. Test Automatic Uploads**
```bash
# Test backend upload
./test-automatic-upload.sh

# Test frontend upload
./upload-frontend-to-server.sh
```

### **4. Test Passwordless Service Management**
```bash
ssh backend-server 'sudo systemctl restart ai-messaging-backend.service'
ssh backend-server 'pm2 restart Frontend'
```

---

## 📊 **Current Status**

| Component | Status | Management | Automation |
|-----------|--------|------------|------------|
| **Backend (FastAPI)** | ✅ Running | systemd | ✅ Automatic |
| **Celery Workers** | ✅ Running | systemd | ✅ Automatic |
| **Frontend (Next.js)** | ✅ Running | PM2 | ✅ Automatic |
| **SSH** | ✅ Working | Passwordless | ✅ Ready |
| **Backend Upload** | ✅ Ready | Automatic | ✅ Complete |
| **Frontend Upload** | ✅ Ready | Automatic | ✅ Complete |
| **Service Restart** | ✅ Ready | Passwordless | ✅ Complete |

---

## 🚀 **Your Complete Workflow**

### **1. Start Development (Backend)**
```bash
./watch-and-upload.sh
```

### **2. Start Development (Frontend)**
```bash
./watch-and-upload-frontend.sh
```

### **3. Edit Files**
- **Backend**: Edit any `.py`, `.txt`, `.yml`, `.json`, `.sh` file
- **Frontend**: Edit any `.tsx`, `.ts`, `.css`, `.json` file

### **4. Automatic Deployment**
- File watchers detect changes
- Files upload to server automatically
- Services restart automatically
- Changes are live instantly

### **5. Monitor Services**
```bash
# Check backend health
curl http://103.215.159.51:8000/health

# Check frontend status
ssh backend-server 'pm2 status Frontend'

# Check backend logs
ssh backend-server 'tail -f logs/fastapi.log'

# Check frontend logs
ssh backend-server 'pm2 logs Frontend'
```

---

## 📁 **File Patterns**

### **Backend (Automatically Uploaded)**
- `*.py` - Python files
- `*.txt` - Text files  
- `*.yml`, `*.yaml` - Configuration files
- `*.json` - JSON files
- `*.sh` - Shell scripts
- `*.md` - Documentation
- `*.env*` - Environment files
- `requirements*.txt` - Python dependencies

### **Frontend (Automatically Uploaded)**
- `*.tsx`, `*.ts` - TypeScript/React files
- `*.css`, `*.scss` - Stylesheets
- `*.json` - Configuration files
- `*.js` - JavaScript files
- `*.md` - Documentation
- `*.env*` - Environment files

### **Excluded from Both**
- `*.log` - Log files
- `*.tmp`, `*.swp` - Temporary files
- `node_modules` - Node.js dependencies
- `.next` - Next.js build output
- `.git` - Git directory
- `venv` - Python virtual environment

---

## 🎉 **You're Fully Automated!**

Your complete system now supports:
- ✅ **Backend automatic uploads** with service restarts
- ✅ **Frontend automatic uploads** with service restarts  
- ✅ **Passwordless SSH** access
- ✅ **VS Code integration** with built-in tasks
- ✅ **File watching** for both frontend and backend
- ✅ **Instant deployment** on every file change

---

**Happy Coding! 🚀**
