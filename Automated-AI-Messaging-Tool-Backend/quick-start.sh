#!/bin/bash

# Quick Start Script for Backend Upload System
# Sets up everything needed for the upload system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 Backend Upload System - Quick Start${NC}"
echo "=============================================="
echo ""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Check if scripts exist
check_scripts() {
    print_status "Checking required scripts..."
    
    local missing_scripts=()
    
    for script in "setup-ssh-keys.sh" "upload-to-server.sh" "watch-and-upload.sh"; do
        if [ ! -f "$script" ]; then
            missing_scripts+=("$script")
        fi
    done
    
    if [ ${#missing_scripts[@]} -gt 0 ]; then
        print_error "Missing scripts: ${missing_scripts[*]}"
        print_info "Please make sure all upload scripts are present in the current directory"
        exit 1
    fi
    
    print_success "All required scripts found"
}

# Make scripts executable
make_executable() {
    print_status "Making scripts executable..."
    
    chmod +x setup-ssh-keys.sh upload-to-server.sh watch-and-upload.sh
    
    print_success "Scripts made executable"
}

# Set up SSH keys
setup_ssh() {
    print_status "Setting up SSH key authentication..."
    
    if [ -f "upload-config.sh" ]; then
        print_warning "SSH keys already configured"
        read -p "Do you want to re-run SSH setup? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Using existing SSH configuration"
            return
        fi
    fi
    
    ./setup-ssh-keys.sh
    
    if [ $? -eq 0 ]; then
        print_success "SSH key authentication set up successfully"
    else
        print_error "SSH key setup failed"
        exit 1
    fi
}

# Test connection
test_connection() {
    print_status "Testing SSH connection..."
    
    if ssh -o ConnectTimeout=10 backend-server "echo 'SSH connection successful'" > /dev/null 2>&1; then
        print_success "SSH connection working"
    else
        print_error "SSH connection failed"
        print_info "Please check your network connection and server availability"
        exit 1
    fi
}

# Test backend health
test_backend() {
    print_status "Testing backend health..."
    
    local health_url="http://103.215.159.51:8000/health"
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$health_url" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        print_success "Backend is healthy"
    else
        print_warning "Backend health check failed (HTTP $response)"
        print_info "This is normal if the backend is not running yet"
    fi
}

# Create staging directory
create_staging() {
    print_status "Creating staging directory..."
    
    mkdir -p toUpload
    mkdir -p uploadBackups
    
    print_success "Staging directories created"
}

# Show usage examples
show_examples() {
    echo ""
    echo -e "${PURPLE}📚 Usage Examples${NC}"
    echo "=================="
    echo ""
    echo -e "${CYAN}Manual Upload:${NC}"
    echo "  ./upload-to-server.sh"
    echo ""
    echo -e "${CYAN}Automatic File Watching:${NC}"
    echo "  ./watch-and-upload.sh"
    echo ""
    echo -e "${CYAN}VS Code/Cursor Tasks:${NC}"
    echo "  Cmd/Ctrl + Shift + P → Tasks: Run Task"
    echo ""
    echo -e "${CYAN}Test Connection:${NC}"
    echo "  ssh backend-server 'echo \"Hello from server\"'"
    echo ""
    echo -e "${CYAN}Check Backend Health:${NC}"
    echo "  curl http://103.215.159.51:8000/health"
    echo ""
}

# Show next steps
show_next_steps() {
    echo ""
    echo -e "${PURPLE}🎯 Next Steps${NC}"
    echo "============="
    echo ""
    echo -e "${GREEN}1. Start Development:${NC}"
    echo "   ./watch-and-upload.sh"
    echo ""
    echo -e "${GREEN}2. Manual Upload:${NC}"
    echo "   ./upload-to-server.sh"
    echo ""
    echo -e "${GREEN}3. VS Code Integration:${NC}"
    echo "   Open Command Palette → Tasks: Run Task"
    echo ""
    echo -e "${GREEN}4. Monitor Backend:${NC}"
    echo "   curl http://103.215.159.51:8000/health"
    echo ""
    echo -e "${GREEN}5. Check Logs:${NC}"
    echo "   ssh backend-server 'tail -f logs/celery.log'"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}🔧 Setting up Backend Upload System...${NC}"
    echo ""
    
    # Check scripts
    check_scripts
    
    # Make executable
    make_executable
    
    # Setup SSH
    setup_ssh
    
    # Test connection
    test_connection
    
    # Test backend
    test_backend
    
    # Create staging
    create_staging
    
    # Show examples
    show_examples
    
    # Show next steps
    show_next_steps
    
    echo ""
    echo -e "${GREEN}🎉 Backend Upload System Setup Complete!${NC}"
    echo "=============================================="
    echo ""
    echo -e "${CYAN}📖 Documentation:${NC} UPLOAD_SYSTEM_README.md"
    echo -e "${CYAN}🔗 Live URL:${NC} http://103.215.159.51:8000"
    echo -e "${CYAN}📚 API Docs:${NC} http://103.215.159.51:8000/docs"
    echo ""
    echo -e "${YELLOW}💡 Tip: Run './watch-and-upload.sh' to start automatic file watching${NC}"
}

# Run main function
main "$@" 