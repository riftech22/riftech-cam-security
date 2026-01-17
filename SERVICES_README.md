# Riftech Security System - Systemd Services

## 🚀 Overview

Sistem ini menggunakan **systemd services** untuk auto-start setelah server reboot. Ada 2 services utama:

1. **security-system-v380.service** - WebSocket server untuk V380 FFmpeg Pipeline
2. **http-server.service** - HTTP server untuk web interface

## 📦 Service Files

### 1. security-system-v380.service

WebSocket server yang menjalankan V380 FFmpeg Pipeline untuk kamera dual-lens.

- **Port**: 8765 (WebSocket)
- **Mode**: V380 FFmpeg (--v380 flag)
- **Auto-restart**: Ya (10 detik setelah crash)
- **Log**: `/root/riftech-cam-security/logs/websocket.log`
- **Error Log**: `/root/riftech-cam-security/logs/websocket_error.log`

### 2. http-server.service

HTTP server yang melayani web interface dan static assets.

- **Port**: 8080 (HTTP)
- **Auto-restart**: Ya (10 detik setelah crash)
- **Log**: `/root/riftech-cam-security/logs/http.log`
- **Error Log**: `/root/riftech-cam-security/logs/http_error.log`

## 🔧 Installation

### Prerequisites

Pastikan:
- Python virtual environment ada di `/root/riftech-cam-security/venv`
- Semua file Python sudah terupdate (`git pull origin main`)
- Firewall mengizinkan ports 8080 dan 8765

### Install Services

Jalankan script instalasi:

```bash
cd /root/riftech-cam-security
sudo ./install_services.sh
```

Script ini akan:
1. ✅ Cek semua requirements
2. ✅ Buat logs directory
3. ✅ Copy service files ke `/etc/systemd/system/`
4. ✅ Stop services lama (jika ada)
5. ✅ Reload systemd
6. ✅ Enable services untuk auto-start
7. ✅ Start services
8. ✅ Cek status services

### Manual Installation (Optional)

Jika ingin menginstall manual:

```bash
# 1. Stop services lama
sudo systemctl stop security-system-v380 2>/dev/null || true
sudo systemctl stop http-server 2>/dev/null || true

# 2. Copy service files
sudo cp security-system-v380.service /etc/systemd/system/
sudo cp http-server.service /etc/systemd/system/

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable services (auto-start on boot)
sudo systemctl enable security-system-v380
sudo systemctl enable http-server

# 5. Start services
sudo systemctl start security-system-v380
sudo systemctl start http-server

# 6. Check status
sudo systemctl status security-system-v380
sudo systemctl status http-server
```

## 📊 Service Management

### Check Status

```bash
# Cek semua status
sudo systemctl status security-system-v380
sudo systemctl status http-server

# Cek apakah running
sudo systemctl is-active security-system-v380
sudo systemctl is-active http-server

# Cek apakah enabled untuk auto-start
sudo systemctl is-enabled security-system-v380
sudo systemctl is-enabled http-server
```

### Start/Stop/Restart

```bash
# Start
sudo systemctl start security-system-v380
sudo systemctl start http-server

# Stop
sudo systemctl stop security-system-v380
sudo systemctl stop http-server

# Restart
sudo systemctl restart security-system-v380
sudo systemctl restart http-server

# Restart keduanya
sudo systemctl restart security-system-v380 http-server
```

### Enable/Disable Auto-start

```bash
# Enable (auto-start pada boot)
sudo systemctl enable security-system-v380
sudo systemctl enable http-server

# Disable (tidak auto-start)
sudo systemctl disable security-system-v380
sudo systemctl disable http-server
```

## 📝 Viewing Logs

### Systemd Journal (Recommended)

```bash
# Live log WebSocket
sudo journalctl -u security-system-v380 -f

# Live log HTTP
sudo journalctl -u http-server -f

# 50 log terakhir
sudo journalctl -u security-system-v380 -n 50
sudo journalctl -u http-server -n 50

# Log sejak boot
sudo journalctl -u security-system-v380 -b
sudo journalctl -u http-server -b

# Log dengan errors only
sudo journalctl -u security-system-v380 -p err
sudo journalctl -u http-server -p err
```

### File Logs

```bash
# WebSocket log
tail -f /root/riftech-cam-security/logs/websocket.log

# HTTP log
tail -f /root/riftech-cam-security/logs/http.log

# Error logs
tail -f /root/riftech-cam-security/logs/websocket_error.log
tail -f /root/riftech-cam-security/logs/http_error.log
```

## 🔍 Troubleshooting

### Service Failed to Start

1. **Cek status:**
   ```bash
   sudo systemctl status security-system-v380
   ```

2. **Lihat log:**
   ```bash
   sudo journalctl -u security-system-v380 -n 50
   ```

3. **Cek Python executable:**
   ```bash
   ls -la /root/riftech-cam-security/venv/bin/python3
   ```

4. **Cek file Python:**
   ```bash
   ls -la /root/riftech-cam-security/web_server.py
   ls -la /root/riftech-cam-security/http_server.py
   ```

5. **Cek logs directory:**
   ```bash
   ls -la /root/riftech-cam-security/logs/
   ```

### Port Already in Use

```bash
# Cek apa yang menggunakan port 8765
sudo netstat -tulpn | grep 8765

# Cek apa yang menggunakan port 8080
sudo netstat -tulpn | grep 8080

# Kill proses jika perlu
sudo kill -9 <PID>
```

### Service Restarting Repeatedly

1. **Lihat log untuk error:**
   ```bash
   sudo journalctl -u security-system-v380 -f
   ```

2. **Cek V380 connection:**
   - Apakah RTSP URL benar?
   - Apakah kamera accessible?
   - Apakah network OK?

3. **Cek dependencies:**
   ```bash
   source /root/riftech-cam-security/venv/bin/activate
   pip list | grep -E "(opencv|ultralytics|websockets)"
   ```

### Service Not Starting on Boot

1. **Cek network dependency:**
   ```bash
   # Service menunggu network-online
   # Pastikan network aktif sebelum services start
   ```

2. **Cek jika enabled:**
   ```bash
   sudo systemctl is-enabled security-system-v380
   sudo systemctl is-enabled http-server
   ```

3. **Manual start untuk test:**
   ```bash
   sudo systemctl start security-system-v380
   sudo systemctl start http-server
   ```

## 🔄 Update Services

### Update Code

```bash
# 1. Pull update
cd /root/riftech-cam-security
git pull origin main

# 2. Restart services untuk load code baru
sudo systemctl restart security-system-v380
sudo systemctl restart http-server

# 3. Cek status
sudo systemctl status security-system-v380
sudo systemctl status http-server
```

### Update Service Configuration

Jika Anda mengubah file service:

```bash
# 1. Copy service file baru
sudo cp security-system-v380.service /etc/systemd/system/
sudo cp http-server.service /etc/systemd/system/

# 2. Reload systemd
sudo systemctl daemon-reload

# 3. Restart services
sudo systemctl restart security-system-v380
sudo systemctl restart http-server
```

## 🗑️ Uninstall Services

```bash
# 1. Stop services
sudo systemctl stop security-system-v380
sudo systemctl stop http-server

# 2. Disable services
sudo systemctl disable security-system-v380
sudo systemctl disable http-server

# 3. Remove service files
sudo rm /etc/systemd/system/security-system-v380.service
sudo rm /etc/systemd/system/http-server.service

# 4. Reload systemd
sudo systemctl daemon-reload

# 5. Reset failed units
sudo systemctl reset-failed
```

## 📋 Quick Reference

| Command | Description |
|---------|-------------|
| `sudo ./install_services.sh` | Install & enable services |
| `sudo systemctl status security-system-v380` | Check WebSocket service status |
| `sudo systemctl status http-server` | Check HTTP service status |
| `sudo systemctl restart security-system-v380` | Restart WebSocket service |
| `sudo systemctl restart http-server` | Restart HTTP service |
| `sudo journalctl -u security-system-v380 -f` | Live log WebSocket |
| `sudo journalctl -u http-server -f` | Live log HTTP |
| `tail -f logs/websocket.log` | File log WebSocket |
| `tail -f logs/http.log` | File log HTTP |

## 🔐 Security Notes

- Services run as **root** user
- Logs are stored in project directory
- Services auto-restart on crash (10 detik delay)
- Network dependency ensures services start after network is up

## 📞 Support

Jika mengalami masalah:

1. Check logs: `sudo journalctl -u security-system-v380 -n 100`
2. Check file logs: `tail -f /root/riftech-cam-security/logs/websocket.log`
3. Check service status: `sudo systemctl status security-system-v380`
4. Restart services: `sudo systemctl restart security-system-v380 http-server`

## 🌐 Access

Setelah services running:

- **Web Interface**: http://10.26.27.104:8080/web.html
- **WebSocket**: ws://10.26.27.104:8765

**Services akan otomatis start setiap kali server reboot!** ✅
