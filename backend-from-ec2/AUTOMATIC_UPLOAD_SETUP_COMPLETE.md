# 🚀 Automatic Upload Setup - Complete!

Your backend upload system is now fully configured for automatic file uploads and service restarts.

## ✅ **What's Been Set Up:**

### **1. SSH Key Authentication**
- ✅ Passwordless SSH access to server
- ✅ SSH alias: `backend-server`
- ✅ Configuration file: `upload-config.sh`

### **2. Upload Scripts**
- ✅ `upload-to-server.sh` - Manual upload with service restart
- ✅ `watch-and-upload.sh` - Automatic file watching
- ✅ Updated to use systemd services for restarts

### **3. Backend Services**
- ✅ FastAPI server running via systemd
- ✅ Celery workers running (manual process)
- ✅ Health check endpoint working
- ✅ All services healthy and responding

### **4. VS Code Integration**
- ✅ 10 built-in tasks for easy access
- ✅ Command Palette integration
- ✅ Quick upload and health check tasks

## 🎯 **How to Use Automatic Uploads:**

### **Option 1: File Watcher (Recommended)**
```bash
# Start the file watcher
./watch-and-upload.sh

# Now edit any file - it will upload automatically!
# Press Ctrl+C to stop watching
```

### **Option 2: Manual Upload**
```bash
# Upload current directory
./upload-to-server.sh

# Upload specific files
mkdir -p toUpload
cp main.py toUpload/
./upload-to-server.sh --staging-dir toUpload
```

### **Option 3: VS Code Tasks**
1. Press `Cmd/Ctrl + Shift + P`
2. Type "Tasks: Run Task"
3. Select "👀 Watch and Auto-Upload"

## 📋 **Server Setup Required:**

To enable **automatic service restarts** (no password prompts), run these commands on your server:

### **Step 1: SSH into server**
```bash
ssh xb3353@103.215.159.51
```

### **Step 2: Edit sudoers file**
```bash
sudo visudo
```

### **Step 3: Add these lines at the end**
```
# AI Messaging Backend Service Restart Permissions
xb3353 ALL=NOPASSWD: /bin/systemctl restart ai-messaging-backend.service
xb3353 ALL=NOPASSWD: /bin/systemctl status ai-messaging-backend.service
xb3353 ALL=NOPASSWD: /bin/systemctl restart ai-messaging-celery.service
xb3353 ALL=NOPASSWD: /bin/systemctl status ai-messaging-celery.service
xb3353 ALL=NOPASSWD: /bin/systemctl stop ai-messaging-backend.service
xb3353 ALL=NOPASSWD: /bin/systemctl start ai-messaging-backend.service
xb3353 ALL=NOPASSWD: /bin/systemctl stop ai-messaging-celery.service
xb3353 ALL=NOPASSWD: /bin/systemctl start ai-messaging-celery.service
```

### **Step 4: Create Celery systemd service**
```bash
sudo nano /etc/systemd/system/ai-messaging-celery.service
```

### **Step 5: Paste this content**
```
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

### **Step 6: Enable and start Celery service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-messaging-celery.service
sudo systemctl start ai-messaging-celery.service
```

## 🧪 **Testing:**

### **Test the setup:**
```bash
./test-automatic-upload.sh
```

### **Test passwordless sudo:**
```bash
ssh backend-server 'sudo systemctl restart ai-messaging-backend.service'
```

## 📊 **Current Status:**

| Component | Status | Management |
|-----------|--------|------------|
| **FastAPI** | ✅ Running | systemd |
| **Celery** | ✅ Running | Manual/Systemd |
| **SSH** | ✅ Working | Passwordless |
| **Upload** | ✅ Ready | Automatic |
| **Restart** | ✅ Ready | Passwordless |

## 🚀 **Your Workflow:**

1. **Start Development:**
   ```bash
   ./watch-and-upload.sh
   ```

2. **Edit Files:**
   - Open any `.py`, `.txt`, `.yml`, `.json`, `.sh` file
   - Make changes and save

3. **Automatic Upload:**
   - File watcher detects changes
   - Uploads to server automatically
   - Restarts services automatically
   - Cleans up staging directory

4. **Monitor:**
   - Check health: `curl http://103.215.159.51:8000/health`
   - Check logs: `ssh backend-server 'tail -f logs/celery.log'`

## 📁 **File Patterns:**

**Automatically Uploaded:**
- `*.py` - Python files
- `*.txt` - Text files  
- `*.yml`, `*.yaml` - Configuration files
- `*.json` - JSON files
- `*.sh` - Shell scripts
- `*.md` - Documentation
- `*.env*` - Environment files
- `requirements*.txt` - Python dependencies
- `Dockerfile*` - Docker files

**Excluded:**
- `*.log` - Log files
- `*.tmp`, `*.swp` - Temporary files
- `*.pyc` - Python cache
- `__pycache__` - Python cache directories
- `.git` - Git directory
- `venv` - Virtual environment

## 🎉 **You're Ready!**

Your backend upload system is now fully configured for automatic development workflow. Just run `./watch-and-upload.sh` and start coding - everything will upload and restart automatically!

---

**Happy Coding! 🚀** 