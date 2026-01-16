# Riftech Cam Security - Ubuntu Server 22 Installation Summary

## 📋 What Was Done

I've analyzed the application and fixed all issues for Ubuntu Server 22 installation. Here's what was improved:

### 🔧 Issues Fixed

1. **Missing Dependencies**: Added ultralytics, torch, websockets to requirements.txt
2. **Headless Installation**: Created automated installer for Ubuntu Server 22
3. **Service Configuration**: Fixed systemd service with proper logging
4. **Startup Script**: Enhanced with error handling and status checks
5. **Documentation**: Created comprehensive Ubuntu Server installation guide

### 📁 New Files Created

1. **install_ubuntu_server.sh** - Automated installation script
2. **UBUNTU_SERVER_README.md** - Complete installation guide
3. **config.example.py** - Configuration template

### 🔄 Modified Files

1. **requirements.txt** - Added missing dependencies
2. **start_web.sh** - Improved error handling and logging
3. **security-system-web.service** - Added logging support

## 🚀 How to Install on Your Ubuntu Server 22 (Proxmox)

### Prerequisites

- Ubuntu Server 22.04 LTS
- IP Address: 10.26.27.104 (as mentioned)
- RTSP Camera: 10.26.27.196 (as configured)
- Internet connection for downloading packages

### Quick Installation (3 Steps)

```bash
# Step 1: Clone repository
cd ~
git clone https://github.com/riftech22/riftech-cam-security.git
cd riftech-cam-security

# Step 2: Run installer
chmod +x install_ubuntu_server.sh
./install_ubuntu_server.sh

# Step 3: Access web interface
# Open browser: http://10.26.27.104:8080/web.html
```

### What the Installer Does

✅ Updates system packages  
✅ Installs Python 3 and dependencies  
✅ Installs OpenCV and AI libraries  
✅ Sets up virtual environment  
✅ Downloads YOLO models  
✅ Configures camera (10.26.27.196)  
✅ Installs systemd service  
✅ Starts service automatically  

## 🎯 Application Features

### Core Features
- **AI Detection**: YOLOv8-powered person detection
- **Face Recognition**: Identify trusted persons
- **Motion Detection**: Advanced motion tracking
- **Security Zones**: Custom polygon-based monitoring
- **RTSP Support**: Works with IP cameras
- **Web Interface**: Access from any browser

### Web Interface Controls
- 🔒 ARM/DISARM system
- ⏺ Start/Stop recording
- 📸 Take snapshots
- 🔇 Mute/unmute alarm
- 🎯 Adjust confidence (15-50%)
- 🤱 Switch YOLO models
- 🦴 Toggle skeleton detection
- 👤 Toggle face recognition
- 📡 Toggle motion boxes
- 🔥 Toggle heat map
- 🌙 Toggle night vision
- ➕ Create custom zones

## 🌐 Access Information

After installation:

```
Web Interface: http://10.26.27.104:8080/web.html
WebSocket:     ws://10.26.27.104:8765
```

## 📊 Service Management

```bash
# Check status
sudo systemctl status security-system-web

# View logs
sudo journalctl -u security-system-web -f

# Restart service
sudo systemctl restart security-system-web

# Stop service
sudo systemctl stop security-system-web

# Start service
sudo systemctl start security-system-web
```

## 🔧 Configuration

### Camera Configuration

Edit `/home/YOUR_USER/riftech-cam-security/config.py`:

```python
# Current configuration (already set):
CAMERA_SOURCE = r"rtsp://admin:Kuncong203@10.26.27.196:554/live/ch00_0"

# For USB camera:
# CAMERA_SOURCE = 0
```

### Performance Tuning

For your server (Ubuntu Server 22 on Proxmox), recommended settings in `config.py`:

```python
# For optimal performance:
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
TARGET_FPS = 25
YOLO_CONFIDENCE = 0.25
performance.yolo_model = 'yolov8n.pt'  # Use Nano model (fastest)
performance.enable_skeleton = False  # Disable to save CPU
performance.enable_heatmap = False  # Disable to save CPU
```

## 📁 Important Directories

```
~/riftech-cam-security/
├── config.py              # Main configuration
├── web_server.py          # WebSocket server
├── install_ubuntu_server.sh  # Installation script
├── start_web.sh           # Startup script
├── requirements.txt       # Python dependencies
├── web.html              # Web interface
├── venv/                 # Virtual environment
├── recordings/           # Video recordings
├── snapshots/            # Screenshots
├── alerts/               # Alert images
├── trusted_faces/        # Trusted person photos
└── logs/                # System logs
    ├── websocket.log
    └── http.log
```

## 🔍 Troubleshooting

### Service Not Starting

```bash
# Check logs
sudo journalctl -u security-system-web -n 50

# Check if ports are in use
netstat -tlnp | grep -E '8080|8765'

# Test camera connection
ffplay rtsp://admin:Kuncong203@10.26.27.196:554/live/ch00_0
```

### High CPU Usage

```bash
# Check CPU usage
htop

# Reduce CPU usage:
# 1. Use yolov8n model (smallest)
# 2. Increase confidence to 30-40%
# 3. Disable skeleton and heatmap
# 4. Reduce FPS to 15-20
```

### Camera Not Connecting

```bash
# Test RTSP connection
ffplay rtsp://admin:Kuncong203@10.26.27.196:554/live/ch00_0

# Check network
ping 10.26.27.196

# Test with OpenCV
python -c "
import cv2
cap = cv2.VideoCapture('rtsp://admin:Kuncong203@10.26.27.196:554/live/ch00_0')
ret, frame = cap.read()
print('Connected!' if ret else 'Failed')
cap.release()
"
```

## 🔒 Security Notes

### Firewall Configuration

```bash
# Allow ports
sudo ufw allow 8080/tcp
sudo ufw allow 8765/tcp

# Only allow specific IPs (recommended)
sudo ufw allow from 10.26.27.0/24 to any port 8080
sudo ufw allow from 10.26.27.0/24 to any port 8765
```

### Default Credentials in Config

⚠️ **IMPORTANT**: The config.py contains:
- RTSP credentials: admin:Kuncong203
- Telegram bot token and chat ID

Consider changing these for production use.

## 📚 Documentation

- **Main README**: `README.md` - Full feature documentation
- **Ubuntu Server Guide**: `UBUNTU_SERVER_README.md` - Detailed installation guide
- **Web Interface**: `WEB_INTERFACE_README.md` - Web interface usage

## 🎉 Next Steps

1. **Install on Ubuntu Server 22**:
   ```bash
   cd ~
   git clone https://github.com/riftech22/riftech-cam-security.git
   cd riftech-cam-security
   ./install_ubuntu_server.sh
   ```

2. **Access Web Interface**:
   - Open browser: http://10.26.27.104:8080/web.html

3. **Create Security Zones**:
   - Click "NEW ZONE"
   - Click "DRAW"
   - Click 3+ points on video
   - Click "DRAW" to complete

4. **ARM System**:
   - Click "ARM SYSTEM"
   - System now monitoring!

5. **Test Detection**:
   - Walk into zone
   - Alarm should trigger
   - Take snapshot to verify

## 📞 Support

- **GitHub Repository**: https://github.com/riftech22/riftech-cam-security
- **Issues**: https://github.com/riftech22/riftech-cam-security/issues

## ✅ Summary

All issues have been fixed and the application is now ready for Ubuntu Server 22 installation on your Proxmox VM at 10.26.27.104.

**Key Improvements:**
- ✅ Automated installation script
- ✅ Complete Ubuntu Server 22 support
- ✅ Headless mode (no GUI required)
- ✅ Systemd service for auto-start
- ✅ Comprehensive documentation
- ✅ All missing dependencies added
- ✅ Changes pushed to GitHub

**Ready to install!** Just run the installer script and access the web interface.
