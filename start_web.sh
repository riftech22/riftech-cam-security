#!/bin/bash

###############################################################################
# Riftech Cam Security - Web Interface Startup Script
# This script starts the web server for headless operation
###############################################################################

set -e

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
echo "║   🛡️  RIFTECH CAM SECURITY - WEB INTERFACE STARTER            ║"
echo "║   Headless Mode for Ubuntu Server                             ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_info "Working directory: $SCRIPT_DIR"
print_info "Current user: $(whoami)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_info "Please run the installation script first: ./install_ubuntu_server.sh"
    exit 1
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Check if Python is available
if ! command -v python &> /dev/null; then
    print_error "Python not found in virtual environment!"
    exit 1
fi

# Check required Python packages
print_info "Checking required Python packages..."
REQUIRED_PACKAGES=("cv2" "numpy" "ultralytics" "websockets" "torch")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    print_error "Missing required packages: ${MISSING_PACKAGES[*]}"
    print_info "Installing missing packages..."
    pip install -r requirements.txt
fi

print_success "All required packages installed"
echo ""

# Kill existing processes
print_info "Cleaning up existing processes..."
pkill -f "python web_server.py" 2>/dev/null || true
pkill -f "python -m http.server" 2>/dev/null || true
sleep 2

print_success "Cleanup complete"
echo ""

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p recordings snapshots alerts trusted_faces logs fixed_images
print_success "Directories created/verified"
echo ""

# Start WebSocket server
print_info "Starting WebSocket server on port 8765..."
python web_server.py > logs/websocket.log 2>&1 &
WS_PID=$!

# Wait for WebSocket server to start
sleep 3

# Check if WebSocket server is running
if ! kill -0 $WS_PID 2>/dev/null; then
    print_error "WebSocket server failed to start!"
    print_error "Check logs: logs/websocket.log"
    cat logs/websocket.log
    exit 1
fi

print_success "WebSocket server started (PID: $WS_PID)"
echo ""

# Start HTTP server for web.html
print_info "Starting HTTP server on port 8080..."
python3 -m http.server 8080 > logs/http.log 2>&1 &
HTTP_PID=$!

# Wait for HTTP server to start
sleep 2

# Check if HTTP server is running
if ! kill -0 $HTTP_PID 2>/dev/null; then
    print_error "HTTP server failed to start!"
    print_error "Check logs: logs/http.log"
    cat logs/http.log
    exit 1
fi

print_success "HTTP server started (PID: $HTTP_PID)"
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

# Display success message
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║               SYSTEM STARTED SUCCESSFULLY!                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
print_success "Riftech Cam Security Web Interface is now running!"
echo ""
echo "Access Information:"
echo "  - Web Interface: http://$SERVER_IP:8080/web.html"
echo "  - WebSocket:     ws://$SERVER_IP:8765"
echo ""
echo "Server PIDs:"
echo "  - WebSocket Server: $WS_PID"
echo "  - HTTP Server:      $HTTP_PID"
echo ""
echo "Log Files:"
echo "  - WebSocket: logs/websocket.log"
echo "  - HTTP:      logs/http.log"
echo ""
print_info "To view logs in real-time:"
echo "  - WebSocket: tail -f logs/websocket.log"
echo "  - HTTP:      tail -f logs/http.log"
echo ""
print_warning "Press Ctrl+C to stop all servers"
echo ""

# Trap for cleanup
trap cleanup SIGINT SIGTERM

cleanup() {
    echo ""
    print_info "Stopping all servers..."
    
    if [ -n "$HTTP_PID" ] && kill -0 $HTTP_PID 2>/dev/null; then
        kill $HTTP_PID 2>/dev/null
        print_success "HTTP server stopped"
    fi
    
    if [ -n "$WS_PID" ] && kill -0 $WS_PID 2>/dev/null; then
        kill $WS_PID 2>/dev/null
        print_success "WebSocket server stopped"
    fi
    
    print_success "All servers stopped. Goodbye!"
    exit 0
}

# Keep script running
while true; do
    # Check if servers are still running
    if ! kill -0 $WS_PID 2>/dev/null; then
        print_error "WebSocket server crashed! Check logs: logs/websocket.log"
        cleanup
    fi
    
    if ! kill -0 $HTTP_PID 2>/dev/null; then
        print_error "HTTP server crashed! Check logs: logs/http.log"
        cleanup
    fi
    
    sleep 5
done
