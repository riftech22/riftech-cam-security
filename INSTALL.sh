#!/bin/bash
###############################################################################
# RifTech Cam Security - Auto Installation Script
# Easy installation for Ubuntu/Debian servers
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
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

print_header() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC} $1"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    else
        print_error "Cannot detect OS"
        exit 1
    fi
    
    print_info "Detected OS: $OS $VERSION"
}

# Update system packages
update_system() {
    print_header "Updating System Packages"
    
    print_info "Updating package lists..."
    apt-get update -y
    
    print_info "Upgrading installed packages..."
    apt-get upgrade -y
    
    print_success "System updated successfully"
}

# Install system dependencies
install_system_deps() {
    print_header "Installing System Dependencies"
    
    print_info "Installing Python 3 and pip..."
    apt-get install -y python3 python3-pip python3-venv
    
    print_info "Installing OpenCV dependencies..."
    apt-get install -y libopencv-dev python3-opencv
    
    print_info "Installing FFmpeg..."
    apt-get install -y ffmpeg
    
    print_info "Installing other dependencies..."
    apt-get install -y git wget curl
    
    print_success "System dependencies installed successfully"
}

# Create project directory
setup_project() {
    print_header "Setting Up Project"
    
    PROJECT_DIR="/opt/riftech-cam-security"
    
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Project directory already exists at $PROJECT_DIR"
        read -p "Do you want to remove it and reinstall? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing project..."
            rm -rf "$PROJECT_DIR"
        else
            print_info "Using existing project directory"
        fi
    fi
    
    if [ ! -d "$PROJECT_DIR" ]; then
        print_info "Creating project directory at $PROJECT_DIR..."
        mkdir -p "$PROJECT_DIR"
    fi
    
    cd "$PROJECT_DIR"
    
    # Clone repository
    if [ ! -d ".git" ]; then
        print_info "Cloning repository..."
        git clone https://github.com/riftech22/riftech-cam-security.git .
    else
        print_info "Pulling latest changes..."
        git pull origin main
    fi
    
    # Create necessary directories
    print_info "Creating necessary directories..."
    mkdir -p logs alerts snapshots recordings trusted_faces
    
    print_success "Project setup completed"
}

# Create virtual environment
setup_venv() {
    print_header "Setting Up Python Virtual Environment"
    
    cd /opt/riftech-cam-security
    
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate venv
    source venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    print_success "Virtual environment ready"
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    cd /opt/riftech-cam-security
    source venv/bin/activate
    
    print_info "Installing requirements..."
    pip install -r requirements.txt
    
    print_success "Python dependencies installed successfully"
}

# Setup configuration
setup_config() {
    print_header "Setting Up Configuration"
    
    cd /opt/riftech-cam-security
    
    if [ ! -f "config.py" ]; then
        print_info "Creating configuration from example..."
        cp config.example.py config.py
        print_warning "Please edit config.py with your settings"
        print_warning "  - Camera RTSP URL"
        print_warning "  - Telegram Bot Token and Chat ID"
    else
        print_info "Configuration file already exists"
    fi
    
    print_success "Configuration ready"
}

# Make scripts executable
make_executable() {
    print_header "Making Scripts Executable"
    
    cd /opt/riftech-cam-security
    
    print_info "Making all .sh scripts executable..."
    chmod +x *.sh 2>/dev/null || true
    
    print_success "Scripts made executable"
}

# Install systemd services
install_services() {
    print_header "Installing Systemd Services"
    
    cd /opt/riftech-cam-security
    
    print_info "Installing systemd service files..."
    cp security-system-v380.service /etc/systemd/system/
    
    print_info "Reloading systemd..."
    systemctl daemon-reload
    
    print_warning "Services installed but NOT enabled"
    print_warning "You can manually start with: ./start_web.sh"
    print_warning "Or enable service: systemctl enable --now security-system-v380.service"
    
    print_success "Systemd services installed"
}

# Run installation verification
verify_installation() {
    print_header "Verifying Installation"
    
    cd /opt/riftech-cam-security
    source venv/bin/activate
    
    # Check Python version
    print_info "Python version: $(python3 --version)"
    
    # Check key packages
    print_info "Checking installed packages..."
    
    python3 << 'EOF'
try:
    import cv2
    print("  ✓ OpenCV installed")
except ImportError:
    print("  ✗ OpenCV NOT installed")

try:
    import numpy
    print("  ✓ NumPy installed")
except ImportError:
    print("  ✗ NumPy NOT installed")

try:
    import websockets
    print("  ✓ WebSockets installed")
except ImportError:
    print("  ✗ WebSockets NOT installed")

try:
    from ultralytics import YOLO
    print("  ✓ Ultralytics YOLO installed")
except ImportError:
    print("  ✗ Ultralytics YOLO NOT installed")

try:
    import telegram
    print("  ✓ Python-telegram-bot installed")
except ImportError:
    print("  ✗ Python-telegram-bot NOT installed")

try:
    import aiohttp
    print("  ✓ AIOHTTP installed")
except ImportError:
    print("  ✗ AIOHTTP NOT installed")
EOF
    
    print_success "Installation verification completed"
}

# Print final instructions
print_instructions() {
    print_header "Installation Complete!"
    
    echo ""
    echo -e "${GREEN}Project installed at: /opt/riftech-cam-security${NC}"
    echo ""
    echo -e "${YELLOW}NEXT STEPS:${NC}"
    echo ""
    echo "1. Edit configuration:"
    echo "   cd /opt/riftech-cam-security"
    echo "   nano config.py"
    echo ""
    echo "2. Update settings in config.py:"
    echo "   - CAMERA_SOURCE: Your camera RTSP URL"
    echo "   - TELEGRAM_BOT_TOKEN: Your Telegram bot token"
    echo "   - TELEGRAM_CHAT_ID: Your Telegram chat ID"
    echo ""
    echo "3. Start the system:"
    echo "   cd /opt/riftech-cam-security"
    echo "   ./start_web.sh"
    echo ""
    echo "4. Access web interface:"
    echo "   http://YOUR_SERVER_IP:8080/web.html"
    echo ""
    echo -e "${YELLOW}ALTERNATIVE COMMANDS:${NC}"
    echo ""
    echo "Start in DEBUG mode (shows all output):"
    echo "   ./debug_run.sh"
    echo ""
    echo "Stop all processes:"
    echo "   ./stop_both_servers.sh"
    echo ""
    echo "Test Telegram bot:"
    echo "   ./test_telegram.sh"
    echo ""
    echo "Check logs:"
    echo "   tail -100 logs/websocket.log"
    echo ""
    echo -e "${GREEN}For detailed documentation, see README.md${NC}"
    echo ""
}

# Main installation flow
main() {
    print_header "RifTech Cam Security - Auto Installation"
    
    echo -e "${YELLOW}This will install RifTech Cam Security on your system${NC}"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
    
    check_root
    detect_os
    update_system
    install_system_deps
    setup_project
    setup_venv
    install_python_deps
    setup_config
    make_executable
    install_services
    verify_installation
    print_instructions
}

# Run main function
main
