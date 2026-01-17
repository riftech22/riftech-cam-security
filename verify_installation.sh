#!/bin/bash
###############################################################################
# RifTech Cam Security - Installation Verification Script
# Verify all components are working correctly
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC} $1"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running from project directory
check_location() {
    if [ ! -f "config.py" ] || [ ! -f "web_server.py" ]; then
        print_error "Please run this script from project directory"
        exit 1
    fi
}

# Check virtual environment
check_venv() {
    print_info "Checking virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found!"
        print_info "Create it with: python3 -m venv venv"
        return 1
    fi
    
    if [ ! -f "venv/bin/python3" ]; then
        print_error "Python3 not found in virtual environment!"
        return 1
    fi
    
    print_success "Virtual environment found"
    return 0
}

# Activate virtual environment
activate_venv() {
    source venv/bin/activate
}

# Check Python version
check_python() {
    print_info "Checking Python version..."
    
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_success "Python: $PYTHON_VERSION"
    
    # Check if Python 3.8+
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python 3.8+ required!"
        return 1
    fi
    
    return 0
}

# Check required Python packages
check_packages() {
    print_info "Checking Python packages..."
    
    python3 << 'EOF'
import sys

packages = {
    'cv2': 'OpenCV',
    'numpy': 'NumPy',
    'websockets': 'WebSockets',
    'aiohttp': 'AIOHTTP',
    'telegram': 'Python-telegram-bot',
}

# Check optional packages
optional_packages = {
    'ultralytics': 'Ultralytics YOLO',
    'mediapipe': 'MediaPipe (Skeleton)',
    'face_recognition': 'Face Recognition',
}

all_installed = True
for module, name in packages.items():
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except ImportError:
        print(f"  ✗ {name} - NOT INSTALLED")
        all_installed = False

for module, name in optional_packages.items():
    try:
        __import__(module)
        print(f"  ✓ {name} (Optional)")
    except ImportError:
        print(f"  ! {name} (Optional) - Not installed")

if not all_installed:
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_success "All required packages installed"
        return 0
    else
        print_error "Some required packages are missing!"
        return 1
    fi
}

# Check configuration file
check_config() {
    print_info "Checking configuration..."
    
    if [ ! -f "config.py" ]; then
        print_error "config.py not found!"
        print_info "Copy from example: cp config.example.py config.py"
        return 1
    fi
    
    print_success "config.py found"
    
    # Check critical settings
    print_info "Checking critical settings..."
    
    python3 << 'EOF'
import config

checks = [
    ('CAMERA_SOURCE', 'Camera source'),
    ('TELEGRAM_BOT_TOKEN', 'Telegram Bot Token'),
    ('TELEGRAM_CHAT_ID', 'Telegram Chat ID'),
]

for attr, name in checks:
    if hasattr(config, attr):
        value = getattr(config, attr)
        if value:
            print(f"  ✓ {name}: Set")
        else:
            print(f"  ! {name}: Not set (optional for camera)")
    else:
        print(f"  ✗ {name}: Missing!")
EOF
    
    print_success "Configuration check completed"
    return 0
}

# Check required directories
check_directories() {
    print_info "Checking directories..."
    
    dirs="logs snapshots recordings alerts trusted_faces"
    
    for dir in $dirs; do
        if [ -d "$dir" ]; then
            print_success "Directory '$dir' exists"
        else
            print_warning "Directory '$dir' not found (will be created on first run)"
        fi
    done
    
    return 0
}

# Check system dependencies
check_system_deps() {
    print_info "Checking system dependencies..."
    
    if command -v ffmpeg &> /dev/null; then
        version=$(ffmpeg -version 2>&1 | head -1)
        print_success "ffmpeg: $version"
    else
        print_error "ffmpeg: NOT INSTALLED"
    fi
    
    if command -v python3 &> /dev/null; then
        version=$(python3 --version 2>&1)
        print_success "python3: $version"
    else
        print_error "python3: NOT INSTALLED"
    fi
    
    # Check FFmpeg for RTSP
    print_info "Checking FFmpeg RTSP support..."
    if ffmpeg -formats 2>/dev/null | grep -q rtsp; then
        print_success "FFmpeg RTSP support: Yes"
    else
        print_warning "FFmpeg RTSP support: Not found (may need recompile)"
    fi
    
    return 0
}

# Test camera connection (if configured)
test_camera() {
    print_info "Testing camera connection..."
    
    python3 << 'EOF'
import config

if not hasattr(config, 'CAMERA_SOURCE'):
    print("  ! Camera not configured")
    exit(0)

camera_url = config.CAMERA_SOURCE
print(f"  Testing: {camera_url}")

try:
    import cv2
    cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)
    
    if not cap.isOpened():
        print("  ✗ Cannot connect to camera")
        print("  ! Check RTSP URL and network connectivity")
        exit(1)
    
    # Try to read a frame
    ret, frame = cap.read()
    if ret:
        print(f"  ✓ Camera connected successfully")
        print(f"  ✓ Resolution: {frame.shape[1]}x{frame.shape[0]}")
    else:
        print("  ✗ Cannot read from camera")
        exit(1)
    
    cap.release()
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    exit(1)
EOF
    
    return $?
}

# Test Telegram bot (if configured)
test_telegram() {
    print_info "Testing Telegram bot..."
    
    python3 << 'EOF'
import config

if not hasattr(config, 'TELEGRAM_BOT_TOKEN') or not config.TELEGRAM_BOT_TOKEN:
    print("  ! Telegram bot not configured")
    exit(0)

try:
    import telegram
    from telegram import Bot
    
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    bot.get_me()
    print("  ✓ Telegram bot connected successfully")
    print(f"  ✓ Bot name: {bot.first_name}")
    
except Exception as e:
    print(f"  ✗ Telegram bot error: {e}")
    print("  ! Check bot token and internet connection")
    exit(1)
EOF
    
    return $?
}

# Check YOLO model
check_yolo() {
    print_info "Checking YOLO model..."
    
    python3 << 'EOF'
try:
    from ultralytics import YOLO
    print("  ✓ Ultralytics YOLO installed")
    
    # Check if model files exist
    import os
    model_files = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt']
    
    found_models = []
    for model in model_files:
        if os.path.exists(model):
            found_models.append(model)
            size = os.path.getsize(model) / (1024*1024)  # MB
            print(f"  ✓ Model: {model} ({size:.1f} MB)")
    
    if not found_models:
        print("  ! No YOLO models found (will download on first run)")
    
except ImportError:
    print("  ✗ Ultralytics YOLO not installed")
    exit(1)
EOF
    
    return $?
}

# Check script permissions
check_scripts() {
    print_info "Checking script permissions..."
    
    scripts="start_web.sh stop_both_servers.sh debug_run.sh INSTALL.sh"
    
    all_executable=true
    for script in $scripts; do
        if [ -f "$script" ]; then
            if [ -x "$script" ]; then
                print_success "$script is executable"
            else
                print_warning "$script is not executable"
                all_executable=false
            fi
        fi
    done
    
    if [ "$all_executable" = true ]; then
        print_success "All scripts are executable"
    else
        print_warning "Run: chmod +x *.sh"
    fi
    
    return 0
}

# Check systemd services
check_systemd() {
    print_info "Checking systemd services..."
    
    if systemctl list-unit-files 2>/dev/null | grep -q "security-system-v380.service"; then
        status=$(systemctl is-enabled security-system-v380.service 2>/dev/null || echo "disabled")
        print_success "security-system-v380.service: $status"
    else
        print_warning "security-system-v380.service: Not installed"
    fi
    
    if systemctl list-unit-files 2>/dev/null | grep -q "http-server.service"; then
        status=$(systemctl is-enabled http-server.service 2>/dev/null || echo "disabled")
        print_success "http-server.service: $status"
    else
        print_warning "http-server.service: Not installed"
    fi
    
    return 0
}

# Main verification flow
main() {
    print_header "RifTech Cam Security - Installation Verification"
    
    # Check location
    check_location || exit 1
    
    # Check virtual environment
    check_venv || exit 1
    
    # Activate venv
    activate_venv
    
    # Run checks
    check_python || exit 1
    check_packages || exit 1
    check_config || exit 1
    check_directories
    check_system_deps
    check_scripts
    check_systemd
    check_yolo || exit 1
    
    # Optional tests
    echo ""
    print_info "Optional Tests (Camera, Telegram)"
    print_warning "These may take a moment..."
    echo ""
    
    test_camera || true  # Don't exit on camera test failure
    test_telegram || true  # Don't exit on telegram test failure
    
    # Summary
    print_header "Verification Complete!"
    
    echo -e "${GREEN}All critical checks passed!${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Edit configuration: nano config.py"
    echo "2. Start system: ./start_web.sh"
    echo "3. Access web interface: http://YOUR_IP:8080/web.html"
    echo ""
    echo -e "${YELLOW}Or run in debug mode:${NC}"
    echo "   ./debug_run.sh"
    echo ""
}

# Run main
main
