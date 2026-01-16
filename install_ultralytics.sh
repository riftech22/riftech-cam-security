#!/bin/bash
# Script untuk install ultralytics dan restart service

echo "================================================"
echo "  INSTALL ULTRALYTICS (YOLOv8)"
echo "================================================"
echo ""

cd ~/riftech-cam-security || exit 1

echo "📦 1. Installing ultralytics..."
pip3 install ultralytics torch torchvision

if [ $? -eq 0 ]; then
    echo "✅ Ultralytics installed successfully"
else
    echo "❌ Failed to install ultralytics"
    exit 1
fi
echo ""

echo "🔄 2. Restarting security-system-web service..."
sudo systemctl restart security-system-web

if [ $? -eq 0 ]; then
    echo "✅ Service restarted"
else
    echo "❌ Failed to restart service"
    exit 1
fi
echo ""

echo "⏳ 3. Waiting for startup (15 seconds)..."
sleep 15
echo ""

echo "📝 4. Checking startup logs..."
echo "---"
tail -30 ~/riftech-cam-security/logs/websocket.log | grep -E '(Detector|Loading|Loaded|YOLO|ultralytics)'
echo "---"
echo ""

echo "🎯 5. Testing YOLO import..."
python3 -c "from ultralytics import YOLO; print('✅ YOLO import OK')" 2>&1
echo ""

echo "================================================"
echo "  INSTALLATION COMPLETE!"
echo "================================================"
echo ""
echo "🌐 Access web interface: http://10.26.27.104:8080/web.html"
echo ""
echo "📖 Check live logs: tail -f ~/riftech-cam-security/logs/websocket.log"
echo ""
