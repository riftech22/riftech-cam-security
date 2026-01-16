#!/usr/bin/env python3
"""Live capture from RTSP and debug split frame detection."""

import cv2
import numpy as np
from ultralytics import YOLO
import time

print("=" * 70, flush=True)
print("Live Split Frame Debug", flush=True)
print("=" * 70, flush=True)
print()

# RTSP URL from config
RTSP_URL = "rtsp://admin:Kuncong203@10.26.27.196:554/"

print(f"Connecting to RTSP stream: {RTSP_URL}", flush=True)
print("Please stand in front of BOTH cameras!", flush=True)
print("Press 's' to capture snapshot and debug", flush=True)
print("Press 'q' to quit", flush=True)
print()

# Open RTSP stream
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("❌ Failed to open RTSP stream!", flush=True)
    print("Trying to open with FFmpeg...", flush=True)
    
    # Try with FFmpeg (handle H.265)
    import subprocess
    import os
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-rtsp_transport', 'tcp',
        '-i', RTSP_URL,
        '-vf', 'scale=1280:720',
        '-pix_fmt', 'bgr24',
        '-f', 'image2pipe',
        '-vcodec', 'rawvideo',
        '-'
    ]
    
    print(f"FFmpeg command: {' '.join(ffmpeg_cmd)}", flush=True)
    
    try:
        pipe = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ FFmpeg pipe opened", flush=True)
        
        # Read frame from FFmpeg
        raw = pipe.stdout.read(1280*720*3)
        frame = np.frombuffer(raw, dtype=np.uint8).reshape(720, 1280, 3)
        
        if frame is not None and frame.size > 0:
            print("✅ Frame captured from FFmpeg!", flush=True)
            
            # Save snapshot
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            snapshot_path = f'snapshots/snap_{timestamp}.jpg'
            cv2.imwrite(snapshot_path, frame)
            print(f"📸 Snapshot saved: {snapshot_path}", flush=True)
            
            # Debug split frame
            h, w = frame.shape[:2]
            mid_y = h // 2
            
            print(f"\nFrame size: {w}x{h}", flush=True)
            print(f"Top frame: (360, 1280, 3)", flush=True)
            print(f"Bottom frame: (360, 1280, 3)", flush=True)
            
            # Split frame
            top_frame = frame[:mid_y, :]
            bottom_frame = frame[mid_y:, :]
            
            # Load model
            print(f"\nLoading YOLO model...", flush=True)
            model = YOLO('yolov8m.pt')
            
            # Detect with VERY LOW confidence
            print(f"\n[1/2] Detecting in TOP frame (conf=0.10)...", flush=True)
            results_top = model(top_frame, conf=0.10, classes=[0], verbose=False)
            top_count = len(results_top[0].boxes) if results_top else 0
            print(f"✅ Top camera persons detected: {top_count}", flush=True)
            
            print(f"\n[2/2] Detecting in BOTTOM frame (conf=0.05)...", flush=True)
            results_bottom = model(bottom_frame, conf=0.05, classes=[0], verbose=False)
            bottom_count = len(results_bottom[0].boxes) if results_bottom else 0
            print(f"✅ Bottom camera persons detected: {bottom_count}", flush=True)
            
            # Draw detections
            output = frame.copy()
            
            # Draw top camera detections
            if results_top and results_top[0].boxes:
                for i, box in enumerate(results_top[0].boxes):
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    conf = float(box.conf[0])
                    print(f"   Top person {i+1}: conf={conf:.2f}, bbox=({x1}, {y1}) -> ({x2}, {y2})", flush=True)
                    cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(output, f"Top{conf:.0%}", (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw bottom camera detections
            if results_bottom and results_bottom[0].boxes:
                for i, box in enumerate(results_bottom[0].boxes):
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    conf = float(box.conf[0])
                    y1_adj = y1 + mid_y
                    y2_adj = y2 + mid_y
                    print(f"   Bottom person {i+1}: conf={conf:.2f}, bbox=({x1}, {y1}) -> ({x2}, {y2}) -> adjusted: ({x1}, {y1_adj}) -> ({x2}, {y2_adj})", flush=True)
                    cv2.rectangle(output, (x1, y1_adj), (x2, y2_adj), (255, 0, 0), 2)
                    cv2.putText(output, f"Bot{conf:.0%}", (x1, y1_adj-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Draw split line
            cv2.line(output, (0, mid_y), (w, mid_y), (0, 255, 255), 3)
            
            # Save debug image
            debug_path = 'live_split_debug.jpg'
            cv2.imwrite(debug_path, output)
            
            print()
            print("=" * 70, flush=True)
            print("✅ Debug Complete!", flush=True)
            print("=" * 70, flush=True)
            print()
            print(f"📊 Results:", flush=True)
            print(f"   Top camera: {top_count} person(s)", flush=True)
            print(f"   Bottom camera: {bottom_count} person(s)", flush=True)
            print(f"   Total: {top_count + bottom_count} person(s)", flush=True)
            print()
            print(f"📸 Snapshot saved: {snapshot_path}", flush=True)
            print(f"📸 Debug image saved: {debug_path}", flush=True)
            print()
            print(f"📋 Check images:", flush=True)
            print(f"   - GREEN boxes = Top camera (0-{mid_y})", flush=True)
            print(f"   - BLUE boxes = Bottom camera ({mid_y}-{h})", flush=True)
            print(f"   - YELLOW line = Split boundary", flush=True)
            print()
            
            # Clean up
            pipe.terminate()
            exit(0)
            
    except Exception as e:
        print(f"❌ FFmpeg error: {e}", flush=True)
        exit(1)

else:
    print("✅ RTSP stream opened!", flush=True)
    
    # Load model
    print(f"\nLoading YOLO model...", flush=True)
    model = YOLO('yolov8m.pt')
    
    while True:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print("⚠️  Failed to read frame, retrying...", flush=True)
            time.sleep(1)
            continue
        
        h, w = frame.shape[:2]
        
        # Split frame
        mid_y = h // 2
        top_frame = frame[:mid_y, :]
        bottom_frame = frame[mid_y:, :]
        
        # Detect with VERY LOW confidence
        results_top = model(top_frame, conf=0.10, classes=[0], verbose=False)
        top_count = len(results_top[0].boxes) if results_top else 0
        
        results_bottom = model(bottom_frame, conf=0.05, classes=[0], verbose=False)
        bottom_count = len(results_bottom[0].boxes) if results_bottom else 0
        
        # Draw detections
        output = frame.copy()
        
        # Draw top camera detections
        if results_top and results_top[0].boxes:
            for box in results_top[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(output, "TOP", (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw bottom camera detections
        if results_bottom and results_bottom[0].boxes:
            for box in results_bottom[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                y1_adj = y1 + mid_y
                y2_adj = y2 + mid_y
                cv2.rectangle(output, (x1, y1_adj), (x2, y2_adj), (255, 0, 0), 2)
                cv2.putText(output, "BOT", (x1, y1_adj-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Draw split line
        cv2.line(output, (0, mid_y), (w, mid_y), (0, 255, 255), 3)
        
        # Draw info
        info = f"Top: {top_count} | Bottom: {bottom_count} | Total: {top_count + bottom_count}"
        cv2.putText(output, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(output, "Press 's' to save snapshot | Press 'q' to quit", (10, h-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Display
        cv2.imshow('Live Split Frame Debug', output)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save snapshot and debug
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            snapshot_path = f'snapshots/snap_{timestamp}.jpg'
            cv2.imwrite(snapshot_path, frame)
            debug_path = f'live_split_debug_{timestamp}.jpg'
            cv2.imwrite(debug_path, output)
            print(f"📸 Snapshot saved: {snapshot_path}", flush=True)
            print(f"📸 Debug saved: {debug_path}", flush=True)
    
    cap.release()
    cv2.destroyAllWindows()
