#!/usr/bin/env python3
"""
Configuration Template for Riftech Cam Security
Copy this file to config.py and modify the settings below
"""

from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any
import os

class AlertType(Enum):
    MOTION = "motion"
    PERSON = "person"
    ZONE_BREACH = "zone_breach"
    FACE_DETECTED = "face_detected"
    SYSTEM = "system"

class Sensitivity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class PerformanceSettings:
    use_gpu: bool = False  # Set to True if you have NVIDIA GPU with CUDA
    use_half_precision: bool = False  # Set to True for faster inference with minor accuracy loss
    enable_skeleton: bool = False  # Pose detection (requires more CPU)
    enable_motion: bool = True  # Motion detection
    enable_heatmap: bool = False  # Heat map visualization
    enable_face_detection: bool = True  # Face recognition
    face_interval: int = 60  # Check faces every N frames
    skeleton_interval: int = 3  # Update skeleton every N frames
    yolo_model: str = 'yolov8n.pt'  # Model: yolov8n.pt (fast), yolov8s.pt (balanced), yolov8m.pt (accurate)

class Config:
    # Base directory and paths
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    RECORDINGS_DIR = BASE_DIR / "recordings"
    SNAPSHOTS_DIR = BASE_DIR / "snapshots"
    ALERTS_DIR = BASE_DIR / "alerts"
    TRUSTED_FACES_DIR = BASE_DIR / "trusted_faces"
    LOGS_DIR = BASE_DIR / "logs"
    DB_PATH = BASE_DIR / "security.db"
    
    # Create directories if they don't exist
    for d in [RECORDINGS_DIR, SNAPSHOTS_DIR, ALERTS_DIR, TRUSTED_FACES_DIR, LOGS_DIR]:
        d.mkdir(exist_ok=True)
    
    # Camera Configuration
    # Options:
    # 1. RTSP camera: rtsp://username:password@IP:PORT/path
    # 2. USB camera: 0, 1, 2, etc. (device number)
    # 3. Video file: /path/to/video.mp4
    
    # V380 Dual-Lens Camera Example:
    # CAMERA_SOURCE = r"rtsp://admin:password@10.26.27.196:554/h264/ch1/main/av_stream"
    CAMERA_SOURCE = r"rtsp://admin:password@192.168.1.100:554/live/ch00_0"
    
    # V380 Dual-Lens Mode
    # Set to True if using V380 dual-lens camera (auto-splits frame vertically)
    V380_MODE = False  # Set to True for V380 cameras
    
    # Video Settings
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    TARGET_FPS = 30
    
    # Detection Settings
    YOLO_CONFIDENCE = 0.25  # Lower = more sensitive, Higher = less sensitive (0.15 - 0.50)
    SKELETON_CONFIDENCE = 0.5
    
    # Face Recognition Settings
    FACE_MATCH_TOLERANCE = 0.6  # Lower = more strict, Higher = more lenient (0.4 - 0.6)
    FACE_DETECTION_SCALE = 0.25  # Scale factor for face detection (0.1 - 1.0)
    
    # Motion Detection Settings
    MOTION_THRESHOLD = 20  # Lower = more sensitive (10 - 50)
    MOTION_MIN_AREA = 300  # Minimum area in pixels to consider as motion
    
    # Timing Settings
    INTRUDER_UPDATE_INTERVAL = 6.0  # Seconds between intruder updates
    ZONE_CLEAR_DELAY = 5.0  # Seconds before zone is considered clear
    
    # Telegram Bot Configuration (Optional)
    # 
    # How to get Telegram Bot Token:
    # 1. Open Telegram and search for @BotFather
    # 2. Send /newbot command
    # 3. Follow instructions to create a bot
    # 4. Copy the token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
    # 
    # How to get Telegram Chat ID:
    # 1. Open Telegram and search for @userinfobot
    # 2. Send /start command
    # 3. Copy your Chat ID (numeric value)
    # 
    # Example:
    # TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    # TELEGRAM_CHAT_ID = "123456789"
    #
    # Leave empty to disable Telegram notifications:
    TELEGRAM_BOT_TOKEN = ""
    TELEGRAM_CHAT_ID = ""
    
    # Audio Settings
    ALARM_FREQUENCY = 880  # Frequency in Hz
    TTS_RATE = 150  # Text-to-speech rate
    TTS_VOLUME = 0.9  # Volume (0.0 - 1.0)
    
    # Other Settings
    TRUSTED_FACES_CHECK_INTERVAL = 60  # Seconds between face checks
    
    # Performance settings
    performance = PerformanceSettings()
    
    # Confidence levels for web interface
    CONFIDENCE_LEVELS: Dict[str, float] = {
        "15%": 0.15,
        "20%": 0.20,
        "25%": 0.25,
        "30%": 0.30,
        "40%": 0.40,
        "50%": 0.50,
        "60%": 0.60,
    }
    
    # Available YOLO models
    AVAILABLE_MODELS: Dict[str, str] = {
        'YOLOv8 Nano (Fast)': 'yolov8n.pt',
        'YOLOv8 Small (Balanced)': 'yolov8s.pt',
        'YOLOv8 Medium (Accurate)': 'yolov8m.pt',
    }
    
    @staticmethod
    def get_sensitivity_settings(sensitivity: Sensitivity) -> Dict[str, Any]:
        """Get preset settings based on sensitivity level"""
        presets = {
            Sensitivity.LOW: {
                'yolo_confidence': 0.50,
                'skeleton_confidence': 0.6,
                'motion_threshold': 30,
                'motion_min_area': 800,
            },
            Sensitivity.MEDIUM: {
                'yolo_confidence': 0.30,
                'skeleton_confidence': 0.5,
                'motion_threshold': 20,
                'motion_min_area': 400,
            },
            Sensitivity.HIGH: {
                'yolo_confidence': 0.15,
                'skeleton_confidence': 0.3,
                'motion_threshold': 12,
                'motion_min_area': 150,
            }
        }
        return presets.get(sensitivity, presets[Sensitivity.MEDIUM])
