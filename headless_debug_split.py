#!/usr/bin/env python3
"""Headless live capture from RTSP and debug split frame detection (NO GUI)."""

import cv2
import numpy as np
from ultralytics import YOLO
import time
import sys

print("=" * 70, flush=True)
print("Headless Live Split Frame Debug (NO GUI)", flush=True)
print("=" * 70, flush=True)
print()

# RTSP URL
RTSP_URL = "rtsp://admin:Kuncong203@10.26.27.196:554/"

print(f"Connecting to RTSP stream: {RTSP_URL}", flush=True)
print("Please stand in front of BOTH cameras!", flush=True)
print("Capturing 10 frames and analyzing...", flush=True)
print()

# Open RTSP stream
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("❌ Failed to open RTSP stream!", flush=True)
    print("Trying with FFmpeg...", flush=True)
    
    # Try with FFmpeg (handle H.265)
    import subprocess
    
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
        
        # Read frames from FFmpeg (capture 5 frames to be sure)
        frame_count = 0
        all_frames = []
        
        while frame_count < 5:
            raw = pipe.stdout.read(1280*720*3)
            if len(raw) != 1280*720*3:
                print(f"⚠️  Frame {frame_count+1}: incomplete data", flush=True)
                continue
            
            frame = np.frombuffer(raw, dtype=np.uint8).reshape(720, 1280, 3)
            if frame is not None and frame.size > 0:
                all_frames.append(frame)
                frame_count += 1
                print(f"✅ Captured frame {frame_count}/5", flush=True)
        
        if len(all_frames) > 0:
            # Use middle frame
            frame = all_frames[len(all_frames)//2]
            
            print(f"\n✅ Captured {len(all_frames)} frames, using middle frame for analysis", flush=True)
            
            # Save snapshot
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            snapshot_path = f'snapshots/headless_snap_{timestamp}.jpg'
            cv2.imwrite(snapshot_path, frame)
            print(f"📸 Snapshot saved: {snapshot_path}", flush=True)
            
            # Debug split frame
            h, w = frame.shape[:2]
            mid_y = h // 2
            
            print(f"\nFrame size: {w}x{h}", flush=True)
            print(f"Split at y={mid_y}", flush=True)
            print(f"Top frame: {mid_y}x{w}", flush=True)
            print(f"Bottom frame: {mid_y}x{w}", flush=True)
            
            # Split frame
            top_frame = frame[:mid_y, :]
            bottom_frame = frame[mid_y:, :]
            
            # Save split frames for visual inspection
            cv2.imwrite(f'snapshots/headless_top_{timestamp}.jpg', top_frame)
            cv2.imwrite(f'snapshots/headless_bottom_{timestamp}.jpg', bottom_frame)
            print(f"📸 Split frames saved: headless_top_{timestamp}.jpg, headless_bottom_{timestamp}.jpg", flush=True)
            
            # Load model
            print(f"\nLoading YOLOv8m model...", flush=True)
            model = YOLO('yolov8m.pt')
            
            # Test different confidence thresholds
            test_thresholds = [(0.25, 0.15), (0.15, 0.10), (0.10, 0.05)]
            
            for idx, (top_conf, bottom_conf) in enumerate(test_thresholds):
                print(f"\n{'='*70}", flush=True)
                print(f"Test {idx+1}: Top conf={top_conf}, Bottom conf={bottom_conf}", flush=True)
                print(f"{'='*70}", flush=True)
                
                # Detect in top frame
                print(f"\n[1/2] Detecting in TOP frame (conf={top_conf})...", flush=True)
                results_top = model(top_frame, conf=top_conf, classes=[0], verbose=False)
                top_count = len(results_top[0].boxes) if results_top else 0
                print(f"   ✅ Top camera persons detected: {top_count}", flush=True)
                
                if top_count > 0 and results_top[0].boxes:
                    for i, box in enumerate(results_top[0].boxes):
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        conf = float(box.conf[0])
                        area = (x2 - x1) * (y2 - y1)
                        print(f"      Person {i+1}: conf={conf:.2f}, bbox=({x1},{y1})->({x2},{y2}), area={area}", flush=True)
                
                # Detect in bottom frame
                print(f"\n[2/2] Detecting in BOTTOM frame (conf={bottom_conf})...", flush=True)
                results_bottom = model(bottom_frame, conf=bottom_conf, classes=[0], verbose=False)
                bottom_count = len(results_bottom[0].boxes) if results_bottom else 0
                print(f"   ✅ Bottom camera persons detected: {bottom_count}", flush=True)
                
                if bottom_count > 0 and results_bottom[0].boxes:
                    for i, box in enumerate(results_bottom[0].boxes):
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        conf = float(box.conf[0])
                        area = (x2 - x1) * (y2 - y1)
                        y1_adj = y1 + mid_y
                        y2_adj = y2 + mid_y
                        print(f"      Person {i+1}: conf={conf:.2f}, bbox=({x1},{y1_adj})->({x2},{y2_adj}), area={area}", flush=True)
                
                print(f"\n   📊 Total: {top_count + bottom_count} person(s)", flush=True)
                
                # If found something, save this version
                if top_count + bottom_count > 0:
                    output = frame.copy()
                    
                    # Draw top detections
                    if results_top and results_top[0].boxes:
                        for box in results_top[0].boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw bottom detections
                    if results_bottom and results_bottom[0].boxes:
                        for box in results_bottom[0].boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                            y1_adj = y1 + mid_y
                            y2_adj = y2 + mid_y
                            cv2.rectangle(output, (x1, y1_adj), (x2, y2_adj), (255, 0, 0), 2)
                    
                    # Draw split line
                    cv2.line(output, (0, mid_y), (w, mid_y), (0, 255, 255), 3)
                    
                    debug_path = f'snapshots/headless_debug_test{idx+1}_{timestamp}.jpg'
                    cv2.imwrite(debug_path, output)
                    print(f"   📸 Debug image saved: {debug_path}", flush=True)
            
            print()
            print("=" * 70, flush=True)
            print("✅ All Tests Complete!", flush=True)
            print("=" * 70, flush=True)
            print()
            print(f"📸 Files saved:", flush=True)
            print(f"   - Original: {snapshot_path}", flush=True)
            print(f"   - Top split: snapshots/headless_top_{timestamp}.jpg", flush=True)
            print(f"   - Bottom split: snapshots/headless_bottom_{timestamp}.jpg", flush=True)
            
            # Clean up
            pipe.terminate()
            exit(0)
            
    except Exception as e:
        print(f"❌ FFmpeg error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        exit(1)
    
else:
    print("✅ RTSP stream opened with cv2.VideoCapture!", flush=True)
    
    # Load model
    print(f"\nLoading YOLOv8m model...", flush=True)
    model = YOLO('yolov8m.pt')
    
    # Capture 10 frames
    frame_count = 0
    all_frames = []
    
    while frame_count < 10:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print(f"⚠️  Failed to read frame {frame_count+1}/10, retrying...", flush=True)
            time.sleep(0.5)
            continue
        
        h, w = frame.shape[:2]
        
        # Only use 1280x720 frames
        if w == 1280 and h == 720:
            all_frames.append(frame)
            frame_count += 1
            print(f"✅ Captured frame {frame_count}/10 ({w}x{h})", flush=True)
        else:
            print(f"⚠️  Skipping frame {frame_count+1} (wrong resolution: {w}x{h})", flush=True)
    
    if len(all_frames) > 0:
        # Use middle frame
        frame = all_frames[len(all_frames)//2]
        
        print(f"\n✅ Captured {len(all_frames)} valid frames, using middle frame for analysis", flush=True)
        
        # Save snapshot
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        snapshot_path = f'snapshots/headless_snap_{timestamp}.jpg'
        cv2.imwrite(snapshot_path, frame)
        print(f"📸 Snapshot saved: {snapshot_path}", flush=True)
        
        # Debug split frame
        h, w = frame.shape[:2]
        mid_y = h // 2
        
        print(f"\nFrame size: {w}x{h}", flush=True)
        print(f"Split at y={mid_y}", flush=True)
        
        # Split frame
        top_frame = frame[:mid_y, :]
        bottom_frame = frame[mid_y:, :]
        
        # Save split frames for visual inspection
        cv2.imwrite(f'snapshots/headless_top_{timestamp}.jpg', top_frame)
        cv2.imwrite(f'snapshots/headless_bottom_{timestamp}.jpg', bottom_frame)
        print(f"📸 Split frames saved: headless_top_{timestamp}.jpg, headless_bottom_{timestamp}.jpg", flush=True)
        
        # Test different confidence thresholds
        test_thresholds = [(0.25, 0.15), (0.15, 0.10), (0.10, 0.05)]
        
        for idx, (top_conf, bottom_conf) in enumerate(test_thresholds):
            print(f"\n{'='*70}", flush=True)
            print(f"Test {idx+1}: Top conf={top_conf}, Bottom conf={bottom_conf}", flush=True)
            print(f"{'='*70}", flush=True)
            
            # Detect in top frame
            print(f"\n[1/2] Detecting in TOP frame (conf={top_conf})...", flush=True)
            results_top = model(top_frame, conf=top_conf, classes=[0], verbose=False)
            top_count = len(results_top[0].boxes) if results_top else 0
            print(f"   ✅ Top camera persons detected: {top_count}", flush=True)
            
            if top_count > 0 and results_top[0].boxes:
                for i, box in enumerate(results_top[0].boxes):
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    conf = float(box.conf[0])
                    area = (x2 - x1) * (y2 - y1)
                    print(f"      Person {i+1}: conf={conf:.2f}, bbox=({x1},{y1})->({x2},{y2}), area={area}", flush=True)
            
            # Detect in bottom frame
            print(f"\n[2/2] Detecting in BOTTOM frame (conf={bottom_conf})...", flush=True)
            results_bottom = model(bottom_frame, conf=bottom_conf, classes=[0], verbose=False)
            bottom_count = len(results_bottom[0].boxes) if results_bottom else 0
            print(f"   ✅ Bottom camera persons detected: {bottom_count}", flush=True)
            
            if bottom_count > 0 and results_bottom[0].boxes:
                for i, box in enumerate(results_bottom[0].boxes):
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    conf = float(box.conf[0])
                    area = (x2 - x1) * (y2 - y1)
                    y1_adj = y1 + mid_y
                    y2_adj = y2 + mid_y
                    print(f"      Person {i+1}: conf={conf:.2f}, bbox=({x1},{y1_adj})->({x2},{y2_adj}), area={area}", flush=True)
            
            print(f"\n   📊 Total: {top_count + bottom_count} person(s)", flush=True)
            
            # If found something, save this version
            if top_count + bottom_count > 0:
                output = frame.copy()
                
                # Draw top detections
                if results_top and results_top[0].boxes:
                    for box in results_top[0].boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw bottom detections
                if results_bottom and results_bottom[0].boxes:
                    for box in results_bottom[0].boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        y1_adj = y1 + mid_y
                        y2_adj = y2 + mid_y
                        cv2.rectangle(output, (x1, y1_adj), (x2, y2_adj), (255, 0, 0), 2)
                
                # Draw split line
                cv2.line(output, (0, mid_y), (w, mid_y), (0, 255, 255), 3)
                
                debug_path = f'snapshots/headless_debug_test{idx+1}_{timestamp}.jpg'
                cv2.imwrite(debug_path, output)
                print(f"   📸 Debug image saved: {debug_path}", flush=True)
        
        print()
        print("=" * 70, flush=True)
        print("✅ All Tests Complete!", flush=True)
        print("=" * 70, flush=True)
        print()
        print(f"📸 Files saved:", flush=True)
        print(f"   - Original: {snapshot_path}", flush=True)
        print(f"   - Top split: snapshots/headless_top_{timestamp}.jpg", flush=True)
        print(f"   - Bottom split: snapshots/headless_bottom_{timestamp}.jpg", flush=True)
    else:
        print("❌ No valid 1280x720 frames captured!", flush=True)
    
    cap.release()
