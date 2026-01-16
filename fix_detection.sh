#!/bin/bash
# Script untuk memperbaiki detection modules

echo "================================================"
echo "  FIX DETECTION MODULES"
echo "================================================"
echo ""

cd ~/riftech-cam-security || exit 1

# Hapus Python cache
echo "🧹 Membersihkan Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✅ Cache dibersihkan"
echo ""

# Cek file detectors.py
echo "📋 Cek detectors.py:"
grep -A 5 "MEDIAPIPE_AVAILABLE = False" detectors.py | head -10
echo ""

# Force pull
echo "📥 Force pulling update..."
git fetch origin main
git reset --hard origin/main
echo "✅ Force update selesai"
echo ""

# Cek version
echo "📋 Versi saat ini:"
git log --oneline -n 3
echo ""

# Restart service
echo "🔄 Restarting service..."
sudo systemctl restart security-system-web
echo ""

# Tunggu 15 detik
echo "⏳ Menunggu 15 detik untuk startup..."
sleep 15
echo ""

# Cek logs
echo "📝 Startup logs:"
head -20 ~/riftech-cam-security/logs/websocket.log | grep -E '(Detector|MediaPipe|Error|Loaded|Loading)'
echo ""

echo "================================================"
echo "  FIX SELESAI!"
echo "================================================"
echo ""
echo "🌐 Akses web interface: http://10.26.27.104:8080/web.html"
echo "📖 Cek logs: tail -f ~/riftech-cam-security/logs/websocket.log"
echo ""
