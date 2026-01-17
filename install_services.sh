#!/bin/bash
# Script untuk menginstall systemd services untuk auto-start pada boot

set -e

echo "=========================================="
echo "  Riftech Security System"
echo "  Install Systemd Services"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: Please run as root (use sudo)"
    exit 1
fi

# Check working directory
WORK_DIR=$(pwd)
if [ ! -f "$WORK_DIR/web_server.py" ]; then
    echo "Error: web_server.py not found"
    echo "Please run this script from project root directory"
    exit 1
fi

echo "[1/6] Checking requirements..."
if [ ! -f "$WORK_DIR/web_server.py" ]; then
    echo "Error: web_server.py not found"
    exit 1
fi

if [ ! -f "$WORK_DIR/http_server.py" ]; then
    echo "Error: http_server.py not found"
    exit 1
fi

if [ ! -d "$WORK_DIR/venv" ]; then
    echo "Error: Virtual environment not found"
    exit 1
fi

echo "      ✓ All requirements found"
echo ""

# Create logs directory
echo "[2/6] Creating logs directory..."
mkdir -p "$WORK_DIR/logs"
echo "      ✓ Logs directory created"
echo ""

# Copy service files
echo "[3/6] Installing systemd services..."
cp "$WORK_DIR/security-system-v380.service" /etc/systemd/system/
cp "$WORK_DIR/http-server.service" /etc/systemd/system/
echo "      ✓ Service files copied to /etc/systemd/system/"
echo ""

# Stop existing services if running
echo "[4/6] Stopping existing services..."
systemctl stop security-system-v380 2>/dev/null || true
systemctl stop http-server 2>/dev/null || true
echo "      ✓ Existing services stopped"
echo ""

# Reload systemd
echo "[5/6] Reloading systemd..."
systemctl daemon-reload
echo "      ✓ Systemd reloaded"
echo ""

# Enable services
echo "[6/6] Enabling services..."
systemctl enable security-system-v380
systemctl enable http-server
echo "      ✓ Services enabled for auto-start"
echo ""

# Start services
echo "[Starting services...]"
systemctl start security-system-v380
systemctl start http-server
echo "      ✓ Services started"
echo ""

# Wait and check status
echo "Checking service status (waiting 5 seconds)..."
sleep 5

echo ""
echo "=========================================="
echo "  Service Status"
echo "=========================================="
echo ""
echo "WebSocket Server (security-system-v380):"
systemctl status security-system-v380 --no-pager -l | head -n 10
echo ""
echo "HTTP Server (http-server):"
systemctl status http-server --no-pager -l | head -n 10
echo ""

# Check if services are running
echo "=========================================="
echo "  Service Status Summary"
echo "=========================================="
echo ""

if systemctl is-active --quiet security-system-v380; then
    echo "✓ WebSocket Server (security-system-v380): RUNNING"
else
    echo "✗ WebSocket Server (security-system-v380): FAILED"
    echo "  Check logs: journalctl -u security-system-v380 -n 50"
fi

if systemctl is-active --quiet http-server; then
    echo "✓ HTTP Server (http-server): RUNNING"
else
    echo "✗ HTTP Server (http-server): FAILED"
    echo "  Check logs: journalctl -u http-server -n 50"
fi

echo ""
echo "=========================================="
echo "  Installation Complete"
echo "=========================================="
echo ""
echo "Services are now configured to auto-start on boot."
echo ""
echo "Access Web Interface:"
echo "  http://10.26.27.104:8080/web.html"
echo ""
echo "View Service Logs:"
echo "  WebSocket: journalctl -u security-system-v380 -f"
echo "  HTTP:      journalctl -u http-server -f"
echo "  Or:        tail -f $WORK_DIR/logs/websocket.log"
echo "            tail -f $WORK_DIR/logs/http.log"
echo ""
echo "Service Management:"
echo "  Start:     sudo systemctl start security-system-v380"
echo "              sudo systemctl start http-server"
echo ""
echo "  Stop:      sudo systemctl stop security-system-v380"
echo "              sudo systemctl stop http-server"
echo ""
echo "  Restart:   sudo systemctl restart security-system-v380"
echo "              sudo systemctl restart http-server"
echo ""
echo "  Status:    sudo systemctl status security-system-v380"
echo "              sudo systemctl status http-server"
echo ""
echo "  Disable:   sudo systemctl disable security-system-v380"
echo "              sudo systemctl disable http-server"
echo ""
echo "=========================================="
