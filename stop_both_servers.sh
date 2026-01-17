#!/bin/bash
# Script untuk menghentikan HTTP dan WebSocket server

echo "=========================================="
echo "  Riftech Security System"
echo "  Stopping Servers"
echo "=========================================="
echo ""

# Stop WebSocket server
echo "[1/2] Stopping WebSocket server..."
pkill -f "python3 web_server.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "      ✓ WebSocket server stopped"
else
    echo "      ℹ WebSocket server not running"
fi

# Stop HTTP server
echo "[2/2] Stopping HTTP server..."
pkill -f "python3 http_server.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "      ✓ HTTP server stopped"
else
    echo "      ℹ HTTP server not running"
fi

echo ""
echo "=========================================="
echo "  All servers stopped"
echo "=========================================="
echo ""
echo "Start again:"
echo "  ./start_both_servers.sh"
echo "  V380 mode: ./start_both_servers.sh --v380"
echo ""
