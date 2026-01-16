# Riftech Cam Security - Ubuntu Server 22 Installation Guide

## 📋 Overview

This guide explains how to install and run the Riftech Cam Security system on Ubuntu Server 22 (headless mode) without GUI.

## 🎯 System Requirements

- **OS**: Ubuntu Server 22.04 LTS or later
- **CPU**: Dual-core 2.0 GHz or better (Quad-core recommended)
- **RAM**: 2 GB minimum (4 GB+ recommended)
- **Storage**: 10 GB+ for application and recordings
- **Network**: 100 Mbps+ for RTSP streaming
- **Camera**: RTSP IP camera or USB camera

## 🚀 Quick Installation

### Automated Installation (Recommended)

The automated installer handles everything:

```bash
# 1. Clone repository
cd ~
git clone https://github.com/riftech22/riftech-cam-security.git
cd riftech-cam-security

# 2. Make installer executable
chmod +x install_ubuntu_server.sh

# 3. Run installer
./install_ubuntu_server.sh
```

The installer will:
- ✅ Update system packages
- ✅ Install Python 3 and dependencies
- ✅ Install OpenCV and AI libraries
- ✅ Set up virtual environment
- ✅ Configure camera settings
- ✅ Install systemd service
- ✅ Start the service automatically

### Manual Installation

If you prefer manual installation:

#### Step 1: System Update

```bash
sudo apt update && sudo apt upgrade -y
```

#### Step 2: Install Python and Development Tools

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-opencv \
    build-essential \
    cmake \
    g++ \
    wget \
    curl \
    git
```

#### Step 3: Install OpenCV Dependencies

```bash
sudo apt install -y \
    libopencv-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    libopenblas-dev \
    liblapack-dev \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    libglib2.0-0
```

#### Step 4: Install Audio Dependencies

```bash
sudo apt install -y \
    portaudio19-dev \
    python3-pyaudio \
    pulseaudio \
    alsa-utils
```

#### Step 5: Install Dlib Dependencies (for Face Recognition)

```bash
sudo apt install -y \
    libboost-python-dev \
    libboost-all-dev
```

#### Step 6: Clone Repository

```bash
cd ~
git clone https://github.com/riftech22/riftech-cam-security.git
cd riftech-cam-security
```

#### Step 7: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 8: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### Step 9: Configure Camera

Edit `config.py`:

```bash
nano config.py
```

Change the camera source:

```python
# For RTSP camera:
CAMERA_SOURCE = r"rtsp://admin:password@YOUR_CAMERA_IP:554/live/ch00_0"

# For USB camera:
CAMERA_SOURCE = 0

# For video file:
CAMERA_SOURCE = "/path/to/video.mp4"
```

#### Step 10: Install and Enable Systemd Service

```bash
# Update service file with your username
sed -i 's/YOUR_USERNAME/$(whoami)/g' security-system-web.service

# Install service
sudo cp security-system-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable security-system-web

# Start service
sudo systemctl start security-system-web
```

## 🔧 Configuration

### Camera Configuration

Edit `config.py` to configure your camera:

```python
# RTSP Camera (IP Camera)
CAMERA_SOURCE = r"rtsp://admin:password@192.168.1.100:554/live/ch00_0"

# USB Camera
CAMERA_SOURCE = 0  # or 1, 2, etc.

# Video File
CAMERA_SOURCE = "/path/to/video.mp4"
```

### Performance Tuning

For optimal performance on your server:

#### Low-End Server (2GB RAM, Dual-core)

```python
# In config.py:
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 15
YOLO_CONFIDENCE = 0.40  # Less sensitive
performance.yolo_model = 'yolov8n.pt'  # Use Nano model
performance.enable_skeleton = False
performance.enable_heatmap = False
```

#### Mid-Range Server (4GB RAM, Quad-core)

```python
# In config.py:
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
TARGET_FPS = 25
YOLO_CONFIDENCE = 0.25
performance.yolo_model = 'yolov8n.pt'
performance.enable_skeleton = False
performance.enable_heatmap = False
```

#### High-End Server (8GB+ RAM, 6+ cores)

```python
# In config.py:
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
TARGET_FPS = 30
YOLO_CONFIDENCE = 0.20
performance.yolo_model = 'yolov8s.pt'  # Use Small model
performance.enable_skeleton = True
performance.enable_heatmap = True
```

### RTSP Camera Settings

For better RTSP performance:

```python
# In web_server.py, modify capture_frame():
self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
```

### Telegram Bot Configuration (Optional)

To receive alerts on Telegram:

1. Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
3. Get your chat ID via [@userinfobot](https://t.me/userinfobot)
4. Update `config.py`:

```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
```

## 🌐 Accessing the Web Interface

Once the service is running:

```bash
# Get server IP
hostname -I

# Access web interface
http://YOUR_SERVER_IP:8080/web.html

# Example:
http://10.26.27.104:8080/web.html
```

### Firewall Configuration

If firewall is enabled:

```bash
# Allow web interface port
sudo ufw allow 8080/tcp

# Allow WebSocket port
sudo ufw allow 8765/tcp

# Check firewall status
sudo ufw status
```

## 🎮 Service Management

### Start/Stop/Restart Service

```bash
# Start service
sudo systemctl start security-system-web

# Stop service
sudo systemctl stop security-system-web

# Restart service
sudo systemctl restart security-system-web
```

### Check Service Status

```bash
# Check status
sudo systemctl status security-system-web

# View logs (last 50 lines)
sudo journalctl -u security-system-web -n 50

# Follow logs in real-time
sudo journalctl -u security-system-web -f
```

### Manual Start (Without Service)

```bash
cd ~/riftech-cam-security
./start_web.sh
```

## 📊 Monitoring and Logs

### Log Files

```bash
# WebSocket logs
tail -f logs/websocket.log

# HTTP logs
tail -f logs/http.log

# Systemd logs
sudo journalctl -u security-system-web -f
```

### System Monitoring

```bash
# Check CPU usage
htop

# Check memory usage
free -h

# Check disk usage
df -h

# Check network connections
netstat -tlnp | grep -E '8080|8765'
```

## 🔍 Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status security-system-web

# View detailed logs
sudo journalctl -u security-system-web -n 100

# Common issues:
# 1. Virtual environment not found → Run ./install_ubuntu_server.sh
# 2. Missing dependencies → pip install -r requirements.txt
# 3. Camera not accessible → Check RTSP URL and network
# 4. Ports already in use → Check with: netstat -tlnp | grep -E '8080|8765'
```

### Camera Not Detected

```bash
# Test camera connection
ffplay rtsp://admin:password@CAMERA_IP:554/live/ch00_0

# Check OpenCV
python -c "import cv2; print(cv2.__version__)"

# Test with Python
python -c "
import cv2
cap = cv2.VideoCapture('rtsp://admin:password@CAMERA_IP:554/live/ch00_0')
ret, frame = cap.read()
print(f'Frame shape: {frame.shape}' if ret else 'No frame')
cap.release()
"
```

### High CPU Usage

```bash
# Check CPU usage
htop

# Solutions:
# 1. Use YOLOv8n model (smallest)
# 2. Increase confidence to 30-40%
# 3. Disable skeleton and heatmap
# 4. Reduce FPS to 15-20
# 5. Lower resolution (640x480)
```

### Out of Memory

```bash
# Check memory
free -h

# Add swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### WebSocket Connection Failed

```bash
# Check if WebSocket is listening
netstat -tlnp | grep 8765

# Check firewall
sudo ufw status

# Allow WebSocket port
sudo ufw allow 8765/tcp

# View logs
tail -f logs/websocket.log
```

### Detection Not Working

```bash
# Check if models downloaded
ls ~/.cache/ultralytics/

# Download models manually
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Test detection
python -c "
from detectors import PersonDetector
from config import Config
config = Config()
detector = PersonDetector(config)
print('Detector initialized successfully')
"
```

## 🔒 Security Best Practices

### 1. Use HTTPS with Nginx (Optional)

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /ws/ {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 2. Configure Firewall

```bash
# Only allow specific IPs
sudo ufw allow from 192.168.1.0/24 to any port 8080
sudo ufw allow from 192.168.1.0/24 to any port 8765

# Block everything else
sudo ufw deny 8080
sudo ufw deny 8765
```

### 3. Regular Updates

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd ~/riftech-cam-security
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## 📁 Directory Structure

```
~/riftech-cam-security/
├── config.py                 # Configuration file
├── web_server.py            # WebSocket server
├── main.py                  # GUI application (not needed for server)
├── install_ubuntu_server.sh # Installation script
├── start_web.sh            # Startup script
├── security-system-web.service # Systemd service
├── requirements.txt        # Python dependencies
├── web.html                # Web interface
│
├── venv/                   # Virtual environment
│
├── recordings/             # Video recordings
├── snapshots/              # Screenshots
├── alerts/                 # Alert images
├── trusted_faces/          # Trusted person photos
├── logs/                   # System logs
│   ├── websocket.log
│   └── http.log
│
└── runs/detect/            # Detection outputs
```

## 🚀 Performance Optimization

### 1. Use PyTorch CPU Version

Already included in installation script for headless servers.

### 2. Optimize OpenCV

```python
# In config.py:
FRAME_WIDTH = 640  # Lower resolution
FRAME_HEIGHT = 480
TARGET_FPS = 15     # Lower FPS
```

### 3. Disable Unnecessary Features

```python
# In config.py:
performance.enable_skeleton = False
performance.enable_heatmap = False
performance.enable_face_detection = False  # If not needed
```

### 4. Use Smaller YOLO Model

```python
# In config.py:
performance.yolo_model = 'yolov8n.pt'  # Fastest
```

## 📞 Support

- **GitHub Issues**: https://github.com/riftech22/riftech-cam-security/issues
- **Documentation**: See `README.md` for full features

## 🎉 Summary

Your Riftech Cam Security system is now running on Ubuntu Server 22!

**Access URLs:**
- Web Interface: `http://YOUR_SERVER_IP:8080/web.html`
- WebSocket: `ws://YOUR_SERVER_IP:8765`

**Useful Commands:**
```bash
# Check status
sudo systemctl status security-system-web

# View logs
sudo journalctl -u security-system-web -f

# Restart service
sudo systemctl restart security-system-web

# Stop service
sudo systemctl stop security-system-web

# Start manually
cd ~/riftech-cam-security && ./start_web.sh
```

**Made with ❤️ by Riftech**
