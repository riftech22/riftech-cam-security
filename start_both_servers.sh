#!/bin/bash
# Script untuk menjalankan HTTP server dan WebSocket server

echo "=========================================="
echo "  Riftech Security System"
echo "  Starting HTTP and WebSocket Servers"
echo "=========================================="
echo ""

# Kill existing processes
echo "[1/5] Killing existing processes..."
pkill -f "python3 web_server.py" 2>/dev/null || true
pkill -f "python3 http_server.py" 2>/dev/null || true
sleep 1
echo "      ✓ Done"
echo ""

# Check V380 mode
V380_MODE=""
if [ "$1" == "--v380" ]; then
    V380_MODE="--v380"
    echo "[2/5] Mode: V380 FFmpeg Pipeline"
else
    echo "[2/5] Mode: Normal Camera"
fi
echo ""

# Start WebSocket server
echo "[3/5] Starting WebSocket server (port 8765)..."
nohup python3 web_server.py $V380_MODE > websocket.log 2>&1 &
WEBSOCKET_PID=$!
echo "      ✓ WebSocket server started (PID: $WEBSOCKET_PID)"
sleep 2
echo ""

# Start HTTP server
echo "[4/5] Starting HTTP server (port 8080)..."
nohup python3 http_server.py > http.log 2>&1 &
HTTP_PID=$!
echo "      ✓ HTTP server started (PID: $HTTP_PID)"
sleep 1
echo ""

# Display status
echo "[5/5] Server Status:"
echo "=========================================="
echo "  WebSocket Server: ws://0.0.0.0:8765 (PID: $WEBSOCKET_PID)"
echo "  HTTP Server:     http://0.0.0.0:8080 (PID: $HTTP_PID)"
echo "=========================================="
echo ""
echo "Access Web Interface:"
echo "  http://YOUR_SERVER_IP:8080/web.html"
echo ""
echo "Monitor Logs:"
echo "  WebSocket: tail -f websocket.log"
echo "  HTTP:      tail -f http.log"
echo ""
echo "Stop Servers:"
echo "  ./stop_both_servers.sh"
echo "  Or: pkill -f 'python3 web_server.py' && pkill -f 'python3 http_server.py'"
echo ""
echo "=========================================="
echo "  Both servers are running!"
echo "=========================================="
