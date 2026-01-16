#!/bin/bash
# Comprehensive diagnostics for YOLOv8 loading issue

echo "================================================"
echo "  YOLOv8 LOADING DIAGNOSTICS"
echo "================================================"
echo ""

cd ~/riftech-cam-security

echo "1. === CHECK VENV ==="
if [ -d "venv" ]; then
    echo "✅ Venv exists"
    source venv/bin/activate
    echo "✅ Venv activated"
    which python
    python --version
else
    echo "❌ Venv not found!"
fi
echo ""

echo "2. === CHECK YOLO IN VENV ==="
if [ -d "venv" ]; then
    python -c "import ultralytics; print('✅ Ultralytics version:', ultralytics.__version__)" 2>&1
    python -c "from ultralytics import YOLO; print('✅ YOLO import OK')" 2>&1
else
    echo "❌ Cannot check - venv not found"
fi
echo ""

echo "3. === CHECK YOLO MODEL FILE ==="
if [ -f "yolov8n.pt" ]; then
    ls -lh yolov8n.pt
    echo "✅ Model file exists"
else
    echo "❌ Model file not found!"
fi
echo ""

echo "4. === SERVICE STATUS ==="
sudo systemctl status security-system-web --no-pager -n 20
echo ""

echo "5. === PROCESSES ==="
echo "Web server process:"
ps aux | grep -E '(web_server|http.server)' | grep -v grep
echo ""

echo "6. === WEBSOCKET LOGS (last 30 lines) ==="
if [ -f "logs/websocket.log" ]; then
    tail -30 logs/websocket.log
else
    echo "❌ Log file not found!"
fi
echo ""

echo "7. === SEARCH FOR YOLO IN LOGS ==="
if [ -f "logs/websocket.log" ]; then
    echo "Looking for YOLO/Detector/MediaPipe messages..."
    grep -i -E '(yolo|detector|loading|loaded|mediapipe)' logs/websocket.log | tail -20
    if [ $? -ne 0 ]; then
        echo "❌ NO YOLO/DETECTOR MESSAGES FOUND IN LOGS!"
    fi
else
    echo "❌ Log file not found!"
fi
echo ""

echo "8. === DETECTOR.PY CHECK ==="
if [ -f "detectors.py" ]; then
    echo "✅ detectors.py exists"
    grep -n "YOLO_AVAILABLE" detectors.py | head -5
    grep -n "Loading yolov8" detectors.py
else
    echo "❌ detectors.py not found!"
fi
echo ""

echo "9. === PYTHON ERROR CHECK ==="
if [ -f "logs/websocket.log" ]; then
    echo "Looking for errors in logs..."
    grep -i -E '(error|exception|traceback|failed)' logs/websocket.log | tail -20
    if [ $? -ne 0 ]; then
        echo "✅ No errors found in logs"
    fi
else
    echo "❌ Log file not found!"
fi
echo ""

echo "================================================"
echo "  DIAGNOSTICS COMPLETE!"
echo "================================================"
echo ""
echo "📋 Summary:"
echo "- Check if venv exists and has ultralytics"
echo "- Check if YOLO can import in venv"
echo "- Check if yolov8n.pt file exists"
echo "- Check service status and processes"
echo "- Check logs for YOLO loading messages"
echo "- Check for errors in logs"
echo ""
