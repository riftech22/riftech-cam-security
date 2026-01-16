#!/bin/bash
# Update script untuk Riftech Cam Security

echo "================================================"
echo "  UPDATE RIFTECH CAM SECURITY"
echo "================================================"
echo ""

cd ~/riftech-cam-security || exit 1

# Cek versi saat ini
echo "📋 Versi saat ini:"
git log --oneline -n 3
echo ""

# Pull update
echo "📥 Pulling update dari GitHub..."
git pull origin main
echo ""

# Cek apakah update berhasil
if [ $? -eq 0 ]; then
    echo "✅ Update berhasil!"
else
    echo "❌ Update gagal!"
    exit 1
fi
echo ""

# Cek latest commit
echo "📋 Versi terbaru:"
git log --oneline -n 1
echo ""

# Restart service
echo "🔄 Restarting service..."
sudo systemctl restart security-system-web
echo ""

# Tunggu 15 detik
echo "⏳ Menunggu 15 detik untuk startup..."
sleep 15
echo ""

# Cek status service
echo "📊 Status service:"
sudo systemctl status security-system-web --no-pager -n 20
echo ""

# Cek logs
echo "📝 Startup logs:"
tail -30 ~/riftech-cam-security/logs/websocket.log | grep -E '(Detector|MediaPipe|Error|Loaded)'
echo ""

echo "================================================"
echo "  UPDATE SELESAI!"
echo "================================================"
echo ""
echo "🌐 Akses web interface: http://10.26.27.104:8080/web.html"
echo "📖 Cek logs: tail -f ~/riftech-cam-security/logs/websocket.log"
echo ""
