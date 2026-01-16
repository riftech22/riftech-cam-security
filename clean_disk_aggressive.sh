#!/bin/bash
# Aggressive disk cleanup untuk membebaskan space

echo "================================================"
echo "  AGGRESSIVE DISK CLEANUP"
echo "================================================"
echo ""

cd ~/riftech-cam-security || exit 1

echo "💾 1. Disk space BEFORE cleanup..."
df -h / | grep -v Filesystem
echo ""

echo "🧹 2. Cleaning up pip cache..."
pip3 cache purge
rm -rf ~/.cache/pip
echo "✅ Pip cache cleaned"
echo ""

echo "🧹 3. Cleaning up apt cache..."
sudo apt-get clean
sudo apt-get autoclean -y
sudo apt-get autoremove -y
echo "✅ APT cache cleaned"
echo ""

echo "🧹 4. Cleaning up Python cache in project..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✅ Python cache cleaned"
echo ""

echo "🧹 5. Cleaning up old detection results..."
if [ -d "runs/detect" ]; then
    ls -lh runs/detect/ | head -20
    echo ""
    echo "Deleting old detection results..."
    rm -rf runs/detect/*
    echo "✅ Detection results cleaned"
fi
echo ""

echo "🧹 6. Cleaning up old recordings..."
if [ -d "recordings" ]; then
    echo "Recordings in folder:"
    ls -lh recordings/*.avi 2>/dev/null | tail -20
    echo ""
    echo "Deleting recordings older than 7 days..."
    find recordings/ -name "*.avi" -mtime +7 -delete 2>/dev/null
    echo "✅ Old recordings deleted"
fi
echo ""

echo "🧹 7. Cleaning up system logs..."
sudo journalctl --vacuum-time=3d
sudo journalctl --vacuum-size=100M
echo "✅ System logs cleaned"
echo ""

echo "🧹 8. Cleaning up system cache..."
sudo rm -rf /var/cache/apt/archives/*.deb
sudo rm -rf /var/lib/apt/lists/*
echo "✅ System cache cleaned"
echo ""

echo "📊 9. Disk space AFTER cleanup..."
df -h / | grep -v Filesystem
echo ""

echo "🎯 10. Finding large files (>50MB)..."
echo "Top 20 largest files:"
find ~/riftech-cam-security -type f -size +50M -exec ls -lh {} \; 2>/dev/null | sort -k5 -hr | head -20
echo ""

echo "================================================"
echo "  CLEANUP COMPLETE!"
echo "================================================"
echo ""
echo "💾 Check available space:"
df -h / | grep -v Filesystem
echo ""
echo "⚠️  If still <1GB free, consider:"
echo "   - Delete more old recordings"
echo "   - Delete runs/detect folders"
echo "   - Extend disk size in Proxmox"
echo ""
