#!/bin/bash
# Script comprehensive untuk check detection modules

echo "================================================"
echo "  CHECK DETECTION MODULES"
echo "================================================"
echo ""

cd ~/riftech-cam-security || exit 1

# Check 1: Python syntax
echo "🐍 1. Check Python syntax..."
python3 -m py_compile detectors.py
if [ $? -eq 0 ]; then
    echo "✅ Python syntax OK"
else
    echo "❌ Python syntax ERROR"
    exit 1
fi
echo ""

# Check 2: Installed packages
echo "📦 2. Check installed packages..."
echo "Ultralytics (YOLO):"
pip3 list | grep -i ultralytics || echo "  ❌ TIDAK terinstall"
echo ""
echo "MediaPipe:"
pip3 list | grep -i mediapipe || echo "  ⚠️  TIDAK terinstall (opsional)"
echo ""

# Check 3: Import test
echo "🧪 3. Test import modules..."
python3 << 'EOF'
import sys
try:
    import cv2
    print("✅ cv2 OK")
except ImportError as e:
    print(f"❌ cv2: {e}")
    sys.exit(1)

try:
    import numpy as np
    print("✅ numpy OK")
except ImportError as e:
    print(f"❌ numpy: {e}")
    sys.exit(1)

try:
    from ultralytics import YOLO
    print("✅ ultralytics (YOLO) OK")
except ImportError as e:
    print(f"❌ ultralytics: {e}")
    sys.exit(1)

try:
    import mediapipe as mp
    print("✅ mediapipe OK")
    if hasattr(mp, 'solutions'):
        print("  - mp.solutions: OK")
    else:
        print("  - mp.solutions: TIDAK ada")
except ImportError:
    print("⚠️  mediapipe TIDAK terinstall (opsional)")
except Exception as e:
    print(f"⚠️  mediapipe error: {e}")
EOF

if [ $? -ne 0 ]; then
    echo "❌ Import test FAILED"
    exit 1
fi
echo ""

# Check 4: Full startup logs
echo "📝 4. Full startup logs:"
echo "---"
head -50 logs/websocket.log
echo "---"
echo ""

# Check 5: Service status
echo "🔧 5. Service status:"
sudo systemctl status security-system-web --no-pager -n 20
echo ""

# Check 6: Git version
echo "📋 6. Git version:"
git log --oneline -n 5
echo ""

echo "================================================"
echo "  CHECK SELESAI"
echo "================================================"
echo ""
