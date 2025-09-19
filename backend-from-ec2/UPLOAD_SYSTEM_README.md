# 🚀 Backend Upload System

A comprehensive upload system for the Python backend project that enables passwordless SSH uploads, automatic file watching, and seamless deployment to the remote server.

## 📋 Features

- **🔑 Passwordless SSH Authentication**: Secure key-based authentication
- **📤 Manual Upload**: Upload files manually with backup and service restart
- **👀 Automatic File Watching**: Watch for changes and auto-upload
- **⚡ VS Code/Cursor Integration**: Built-in tasks for easy access
- **🔄 Service Management**: Automatic backend service restart
- **📁 File Organization**: Staging directories and cleanup
- **🎨 Colored Output**: Beautiful terminal interface with status indicators

## 🛠️ Setup

### 1. Initial Setup

```bash
# Make scripts executable
chmod +x setup-ssh-keys.sh upload-to-server.sh watch-and-upload.sh

# Set up SSH key authentication
./setup-ssh-keys.sh
```

### 2. Configuration

The setup script creates `upload-config.sh` with all necessary configuration:

```bash
# Load configuration
source upload-config.sh

# Test connection
ssh backend-server 'echo "Connection successful"'
```

## 📤 Upload Methods

### Method 1: Manual Upload

```bash
# Upload current directory
./upload-to-server.sh

# Upload without backup (faster)
./upload-to-server.sh --no-backup

# Upload from staging directory
./upload-to-server.sh --staging-dir toUpload

# Upload specific files
mkdir -p toUpload
cp main.py toUpload/
./upload-to-server.sh --staging-dir toUpload
```

### Method 2: Automatic File Watching

```bash
# Start file watcher
./watch-and-upload.sh

# Custom configuration
./watch-and-upload.sh --watch-dirs src,tests --debounce 10 --max-frequency 60
```

### Method 3: VS Code/Cursor Tasks

1. Open Command Palette (`Cmd/Ctrl + Shift + P`)
2. Type "Tasks: Run Task"
3. Select one of the available tasks:
   - 🔑 Setup SSH Keys
   - 📤 Upload to Server
   - ⚡ Quick Upload
   - 👀 Watch and Auto-Upload
   - 🔍 Test SSH Connection
   - 🌐 Check Backend Health

## 📁 File Organization

### Staging Directory Structure

```
toUpload/
├── main.py
├── celery_app.py
├── requirements.txt
├── celery_tasks/
│   ├── file_tasks.py
│   ├── scraping_tasks.py
│   └── form_submission_tasks.py
├── database/
│   ├── database_manager.py
│   └── models.py
└── ai/
    └── message_generator.py
```

### Backup Directory

```
uploadBackups/
├── 20241230_143022/
├── 20241230_143156/
└── 20241230_143245/
```

## 🔧 Configuration

### Server Details

- **Host**: 103.215.159.51
- **User**: xb3353
- **Remote Path**: /home/xb3353/Automated-AI-Messaging-Tool-Backend
- **Port**: 8000
- **SSH Alias**: backend-server

### File Patterns

**Uploaded Files:**
- `*.py` - Python files
- `*.txt` - Text files
- `*.yml`, `*.yaml` - Configuration files
- `*.json` - JSON files
- `*.sh` - Shell scripts
- `*.md` - Documentation
- `*.env*` - Environment files
- `requirements*.txt` - Python dependencies
- `Dockerfile*` - Docker files
- `*.config`, `*.conf` - Configuration files

**Excluded Files:**
- `*.log` - Log files
- `*.tmp`, `*.swp` - Temporary files
- `*.pyc` - Python cache
- `__pycache__` - Python cache directories
- `.git` - Git directory
- `venv` - Virtual environment
- `node_modules` - Node modules
- `.next` - Next.js build
- `.env.local` - Local environment

## 🚀 Usage Examples

### Quick Development Workflow

```bash
# 1. Set up SSH keys (one-time)
./setup-ssh-keys.sh

# 2. Start file watcher for automatic uploads
./watch-and-upload.sh

# 3. Edit files - they'll be uploaded automatically
# 4. Check server status
ssh backend-server 'ps aux | grep python'
```

### Manual Upload Workflow

```bash
# 1. Make changes to files
# 2. Upload with backup
./upload-to-server.sh

# 3. Check if service is running
curl http://103.215.159.51:8000/health
```

### VS Code/Cursor Integration

1. **Setup**: Run "🔑 Setup SSH Keys" task
2. **Development**: Use "👀 Watch and Auto-Upload" task
3. **Manual Upload**: Use "📤 Upload to Server" task
4. **Quick Upload**: Use "⚡ Quick Upload" task
5. **Health Check**: Use "🌐 Check Backend Health" task

## 🔍 Monitoring

### Check Service Status

```bash
# Check if backend is running
curl http://103.215.159.51:8000/health

# Check server processes
ssh backend-server 'ps aux | grep -E "(uvicorn|celery|python.*main)"'

# Check logs
ssh backend-server 'tail -f logs/celery.log'
```

### Health Check Endpoints

- **Health**: `http://103.215.159.51:8000/health`
- **API Docs**: `http://103.215.159.51:8000/docs`
- **Live URL**: `http://103.215.159.51:8000`

## 🛠️ Troubleshooting

### SSH Connection Issues

```bash
# Test SSH connection
ssh backend-server 'echo "Connection successful"'

# If failed, re-run setup
./setup-ssh-keys.sh
```

### Upload Issues

```bash
# Check if files exist
ls -la setup-ssh-keys.sh upload-to-server.sh

# Check permissions
ls -la *.sh

# Re-run setup
./setup-ssh-keys.sh
```

### Service Issues

```bash
# Check if service is running
ssh backend-server 'ps aux | grep python'

# Restart service manually
ssh backend-server 'cd /home/xb3353/Automated-AI-Messaging-Tool-Backend && ./start_local.sh'

# Check logs
ssh backend-server 'tail -f logs/celery.log'
```

## 📊 Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup-ssh-keys.sh` | SSH key setup | One-time setup |
| `upload-to-server.sh` | Manual upload | Development uploads |
| `watch-and-upload.sh` | File watcher | Automatic uploads |
| `ecosystem.config.js` | PM2 config | Production deployment |

## 🎯 Best Practices

1. **Always backup before major changes**: Use `--no-backup` only for quick fixes
2. **Use staging directory**: Copy files to `toUpload/` for organized uploads
3. **Monitor logs**: Check `logs/celery.log` for any issues
4. **Test health endpoint**: Verify service is running after upload
5. **Use VS Code tasks**: Leverage built-in tasks for convenience

## 🔄 Workflow Integration

### Development Workflow

1. **Setup**: Run `./setup-ssh-keys.sh` once
2. **Development**: Use `./watch-and-upload.sh` for automatic uploads
3. **Testing**: Use VS Code tasks for quick operations
4. **Deployment**: Use `./upload-to-server.sh` for manual control

### Production Workflow

1. **Manual Upload**: `./upload-to-server.sh`
2. **Health Check**: `curl http://103.215.159.51:8000/health`
3. **Log Monitoring**: `ssh backend-server 'tail -f logs/celery.log'`

## 📝 Notes

- The system automatically restarts the backend service after upload
- File watcher has debouncing to prevent excessive uploads
- SSH keys are stored in `~/.ssh/backend_upload_key`
- Configuration is stored in `upload-config.sh`
- Backups are created in `uploadBackups/` directory
- Staging files are cleaned up after successful upload

## 🆘 Support

If you encounter issues:

1. Check SSH connection: `ssh backend-server 'echo "test"`
2. Check service health: `curl http://103.215.159.51:8000/health`
3. Check logs: `ssh backend-server 'tail -f logs/celery.log'`
4. Re-run setup: `./setup-ssh-keys.sh`

---

**Happy Uploading! 🚀** 