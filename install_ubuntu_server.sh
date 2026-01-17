#!/bin/bash

###############################################################################
# Riftech Cam Security - Ubuntu Server 22 Installation Script
# This script installs security system for headless Ubuntu Server 22 with V380 support
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🛡️  RIFTECH CAM SECURITY - UBUNTU SERVER INSTALLER          ║"
echo "║   Headless Installation for Ubuntu Server 22                 ║"
echo "║   V380 Dual-Lens Camera Support                              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Get current user (works for both root and normal users)
if [ "$EUID" -eq 0 ]; then
    CURRENT_USER="root"
    CURRENT_HOME="/root"
    print_warning "Running as root user."
else
    CURRENT_USER=$(whoami)
    CURRENT_HOME=$(eval echo ~$CURRENT_USER)
fi

print_info "Installation user: $CURRENT_USER"
print_info "Home directory: $CURRENT_HOME"
echo ""

# Ask for camera configuration
print_warning "Camera Configuration"
read -p "Enter RTSP URL (default: rtsp://admin:password@IP:554/live): " RTSP_URL
read -p "Enter server IP address (default: 10.26.27.104): " SERVER_IP

# Set defaults if empty
RTSP_URL=${RTSP_URL:-"rtsp://admin:Kuncong203@10.26.27.196:554/h264/ch1/main/av_stream"}
SERVER_IP=${SERVER_IP:-"10.26.27.104"}

echo ""
print_info "Camera RTSP URL: $RTSP_URL"
print_info "Server IP: $SERVER_IP"
echo ""

# Ask for V380 mode
print_warning "Camera Type"
read -p "Is this a V380 dual-lens camera? (y/n, default: y): " V380_MODE
V380_MODE=${V380_MODE:-"y"}
if [ "$V380_MODE" = "y" ] || [ "$V380_MODE" = "Y" ]; then
    V380_MODE_ENABLED=true
    print_success "V380 dual-lens mode enabled"
else
    V380_MODE_ENABLED=false
    print_info "Normal camera mode"
fi
echo ""

# Ask for Telegram configuration
print_warning "Telegram Configuration (Optional)"
echo "Leave empty to skip Telegram integration"
read -p "Enter Telegram Bot Token (from @BotFather): " TELEGRAM_BOT_TOKEN
read -p "Enter Telegram Chat ID (from @userinfobot): " TELEGRAM_CHAT_ID

echo ""
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    print_success "Telegram integration enabled"
    print_info "Bot Token: ${TELEGRAM_BOT_TOKEN:0:20}..."
    print_info "Chat ID: $TELEGRAM_CHAT_ID"
else
    print_warning "Telegram integration skipped (empty credentials)"
fi
echo ""

# Step 1: Update system
print_info "Step 1/8: Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

# Step 2: Install Python and development tools
print_info "Step 2/8: Installing Python and development tools..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-opencv \
    build-essential \
    cmake \
    g++ \
    wget \
    curl \
    ffmpeg

print_success "Python and development tools installed"

# Step 3: Install OpenCV dependencies (headless version)
print_info "Step 3/8: Installing OpenCV dependencies..."
sudo apt install -y \
    libopencv-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    libopenblas-dev \
    liblapack-dev \
    libgomp1

print_success "OpenCV dependencies installed"

# Step 4: Install audio dependencies
print_info "Step 4/8: Installing audio dependencies..."
sudo apt install -y \
    portaudio19-dev \
    python3-pyaudio \
    pulseaudio \
    alsa-utils

print_success "Audio dependencies installed"

# Step 5: Install additional system dependencies
print_info "Step 5/8: Installing additional dependencies..."
sudo apt install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    libglib2.0-0 \
    git

print_success "Additional dependencies installed"

# Step 6: Install dlib dependencies for face recognition
print_info "Step 6/8: Installing dlib dependencies..."
sudo apt install -y \
    libboost-python-dev \
    libboost-all-dev

print_success "dlib dependencies installed"

# Step 7: Clone repository (if not already in directory)
print_info "Step 7/8: Setting up project directory..."

if [ ! -d ".git" ]; then
    print_info "Cloning repository..."
    git clone https://github.com/riftech22/riftech-cam-security.git
    cd riftech-cam-security
else
    print_info "Repository already exists, updating..."
    git pull origin main
    cd "$(dirname "$0")"
fi

# Create virtual environment
print_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_info "Installing Python dependencies (this may take 10-20 minutes)..."
pip install -r requirements.txt

# Install PyTorch CPU version (for server without GPU)
print_info "Installing PyTorch CPU version..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

print_success "Python dependencies installed"

# Step 8: Configure application
print_info "Step 8/8: Configuring application..."

# Copy config.example.py to config.py if config.py doesn't exist
if [ ! -f "config.py" ]; then
    print_info "Creating config.py from template..."
    cp config.example.py config.py
fi

# Update config.py with RTSP URL
print_info "Updating camera configuration..."
sed -i "s|CAMERA_SOURCE =.*|CAMERA_SOURCE = r\"$RTSP_URL\"|g" config.py

# Update config.py with V380 mode
if [ "$V380_MODE_ENABLED" = true ]; then
    print_info "Enabling V380 mode in config..."
    sed -i 's/V380_MODE = False/V380_MODE = True/g' config.py
    print_success "V380 mode enabled"
fi

# Update config.py with Telegram credentials if provided
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    print_info "Updating Telegram configuration..."
    sed -i "s|TELEGRAM_BOT_TOKEN =.*|TELEGRAM_BOT_TOKEN = \"$TELEGRAM_BOT_TOKEN\"|g" config.py
    sed -i "s|TELEGRAM_CHAT_ID =.*|TELEGRAM_CHAT_ID = \"$TELEGRAM_CHAT_ID\"|g" config.py
    print_success "Telegram configuration updated"
fi

print_success "Configuration updated"

# Create directories
print_info "Creating necessary directories..."
mkdir -p recordings snapshots alerts trusted_faces logs

print_success "Directories created"

# Test RTSP connection
print_info "Testing RTSP connection (optional, press Ctrl+C to skip)..."
timeout 5 ffprobe -v quiet -print_format json -show_streams "$RTSP_URL" 2>/dev/null > /tmp/rtsp_test.json || print_warning "RTSP connection test failed (will retry on first run)"
if [ -f "/tmp/rtsp_test.json" ]; then
    print_success "RTSP connection successful!"
    rm /tmp/rtsp_test.json
fi

# Make scripts executable
print_info "Making scripts executable..."
chmod +x start_both_servers.sh
chmod +x stop_both_servers.sh
chmod +x install_services.sh
chmod +x install_ubuntu_server.sh

print_success "Scripts made executable"

# Download YOLO models
print_info "Downloading YOLO models (first run only)..."
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')" 2>/dev/null || print_warning "YOLOv8s model download failed (will download on first run)"

print_success "Setup complete!"
echo ""

# Test server startup
print_info "Testing server startup (5 seconds)..."
./start_both_servers.sh &
SERVER_PID=$!
sleep 5

# Check if servers are running
if pgrep -f "web_server.py" > /dev/null && pgrep -f "http_server.py" > /dev/null; then
    print_success "Servers started successfully!"
    echo ""
    print_warning "Stopping test servers..."
    pkill -f "web_server.py"
    pkill -f "http_server.py"
    sleep 2
else
    print_warning "Server startup test failed (check logs: logs/websocket.log)"
fi

# Final summary
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                   INSTALLATION COMPLETE!                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
print_success "Installation completed successfully!"
echo ""
echo "Configuration:"
echo "  - User: $CURRENT_USER"
echo "  - Server IP: $SERVER_IP"
echo "  - Camera RTSP: $RTSP_URL"
echo "  - Camera Type: $([ "$V380_MODE_ENABLED" = true ] && echo "V380 Dual-Lens" || echo "Normal Camera")"
echo "  - Telegram Integration: $([ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ] && echo "Enabled" || echo "Disabled")"
echo "  - Project directory: $CURRENT_HOME/riftech-cam-security"
echo ""
echo "Access URLs:"
echo "  - Web Interface: http://$SERVER_IP:8080/web.html"
echo "  - WebSocket: ws://$SERVER_IP:8765"
echo ""
echo "Commands:"
echo "  - Start manually: ./start_both_servers.sh"
echo "  - Install services: sudo ./install_services.sh"
echo "  - Start service: sudo systemctl start security-system-v380"
echo "  - Stop service: sudo systemctl stop security-system-v380"
echo "  - Restart service: sudo systemctl restart security-system-v380"
echo "  - Check status: sudo systemctl status security-system-v380"
echo "  - View logs: sudo journalctl -u security-system-v380 -f"
echo ""
print_warning "IMPORTANT: Make sure your RTSP camera is accessible from this server"
echo ""
print_info "To enable auto-start on boot, run: sudo ./install_services.sh"
echo ""
print_info "To start servers manually, run: ./start_both_servers.sh"
echo ""
