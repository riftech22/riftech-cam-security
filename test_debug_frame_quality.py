#!/usr/bin/env python3
"""Debug frame quality and detection with optimal confidence."""

import cv2
import numpy as np
from ultralytics import YOLO
import time

print("=" * 70, flush=True)
print("Debug Frame Quality & Detection", flush=True)
print("=" * 70, flush=True)
print()

# RTSP URL
RTSP_URL = "rtsp://admin:Kuncong203@10.26.27.196:554/"

print(f"Connecting to RTSP: {RTSP_URL}", flush=True)
print("Testing confidence 0.25 with frame quality check...", flush=True)
print()

# Open RTSP
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("❌ Failed to open RTSP stream!", flush=True)
    exit(1)

print("✅ RTSP opened!", flush=True)

# Load YOLOv8m model
print("\nLoading YOLOv8m model...", flush=True)
model = YOLO('yolov8m.pt')

# Test 10 frames
frames_processed = 0
best_frame = None
best_persons = 0

while frames_processed < 10:
    ret, frame = cap.read()
    
    if not ret or frame is None:
        print(f"⚠️  Failed to read frame {frames_processed+1}/10", flush=True)
        time.sleep(0.3)
        continue
    
    original_h, original_w = frame.shape[:2]
    
    # Save original frame for inspection
    cv2.imwrite(f'debug_frame_{frames_processed+1}_original.jpg', frame)
    
    print(f"\nFrame {frames_processed+1}/10", flush=True)
    print(f"   Original: {original_w}x{original_h}", flush=True)
    
    # Preprocessing (resize + brightness + CLAHE)
    frame_resized = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_LINEAR)
    
    # Calculate brightness statistics
    brightness = np.mean(frame_resized)
    std_dev = np.std(frame_resized)
    
    print(f"   Brightness: {brightness:.1f}, Std: {std_dev:.1f}", flush=True)
    
    # Save resized frame
    cv2.imwrite(f'debug_frame_{frames_processed+1}_resized.jpg', frame_resized)
    
    # Brightness adjustment
    if brightness > 120:
        frame_adjusted = cv2.convertScaleAbs(frame_resized, alpha=0.7, beta=-30)
        print(f"   Adjusted: Overexposed (brightness > 120)", flush=True)
    elif brightness < 50:
        frame_adjusted = cv2.convertScaleAbs(frame_resized, alpha=1.3, beta=30)
        print(f"   Adjusted: Underexposed (brightness < 50)", flush=True)
    else:
        frame_adjusted = frame_resized.copy()
        print(f"   Adjusted: Normal brightness", flush=True)
    
    # CLAHE
    lab = cv2.cvtColor(frame_adjusted, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    frame_processed = cv2.merge([l, a, b])
    frame_processed = cv2.cvtColor(frame_processed, cv2.COLOR_LAB2BGR)
    
    # Save processed frame
    cv2.imwrite(f'debug_frame_{frames_processed+1}_processed.jpg', frame_processed)
    
    # Split frame
    h, w = frame_processed.shape[:2]
    mid_y = h // 2
    top_frame = frame_processed[:mid_y, :]
    bottom_frame = frame_processed[mid_y:, :]
    
    # Save split frames
    cv2.imwrite(f'debug_frame_{frames_processed+1}_top.jpg', top_frame)
    cv2.imwrite(f'debug_frame_{frames_processed+1}_bottom.jpg', bottom_frame)
    
    print(f"   Split: Top (0-{mid_y}), Bottom ({mid_y}-{h})", flush=True)
    
    # Detect with confidence 0.25
    results_top = model(top_frame, conf=0.25, classes=[0], verbose=False)
    results_bottom = model(bottom_frame, conf=0.25, classes=[0], verbose=False)
    
    top_count = len(results_top[0].boxes) if results_top and results_top[0].boxes else 0
    bottom_count = len(results_bottom[0].boxes) if results_bottom and results_bottom[0].boxes else 0
    total_count = top_count + bottom_count
    
    print(f"   Detection (conf=0.25): {total_count} persons (top: {top_count}, bottom: {bottom_count})", flush=True)
    
    if total_count > 0:
        # Draw detections
        for box in results_top[0].boxes if results_top and results_top[0].boxes else []:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            conf = float(box.conf[0])
            cv2.rectangle(frame_processed, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(frame_processed, f"{conf:.2f}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        for box in results_bottom[0].boxes if results_bottom and results_bottom[0].boxes else []:
            x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            conf = float(box.conf[0])
            y1_adj = y1 + mid_y
            y2_adj = y2 + mid_y
            cv2.rectangle(frame_processed, (x1, y1_adj), (x2, y2_adj), (0, 255, 0), 3)
            cv2.putText(frame_processed, f"{conf:.2f}", (x1, y1_adj-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imwrite(f'debug_frame_{frames_processed+1}_detected.jpg', frame_processed)
        
        # Keep best result
        if total_count > best_persons:
            best_persons = total_count
            best_frame = frame_processed.copy()
            print(f"   ✅ NEW BEST: {total_count} persons!", flush=True)
    
    frames_processed += 1
    time.sleep(0.5)

cap.release()

print()
print("=" * 70, flush=True)
print("✅ Test Complete!", flush=True)
print("=" * 70, flush=True)
print()

if best_frame is not None and best_persons > 0:
    print(f"🎯 BEST RESULT: {best_persons} person(s) detected!", flush=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(f'debug_best_{timestamp}.jpg', best_frame)
    print(f"📸 Best frame saved: debug_best_{timestamp}.jpg", flush=True)
else:
    print(f"❌ No persons detected in {frames_processed} frames", flush=True)

print()
print("📁 FILES SAVED FOR INSPECTION:", flush=True)
print("   - debug_frame_*_original.jpg (2304x2592 - from RTSP)", flush=True)
print("   - debug_frame_*_resized.jpg (1280x720 - after resize)", flush=True)
print("   - debug_frame_*_processed.jpg (1280x720 - after brightness+CLAHE)", flush=True)
print("   - debug_frame_*_top.jpg (640x360 - top half)", flush=True)
print("   - debug_frame_*_bottom.jpg (640x360 - bottom half)", flush=True)
print("   - debug_frame_*_detected.jpg (1280x720 - with bounding boxes)", flush=True)
print()
print("💡 RECOMMENDATIONS:", flush=True)
print("   1. Check the saved images", flush=True)
print("   2. Verify you're standing in front of camera", flush=True)
print("   3. If no detections, confidence might be too high", flush=True)
print("   4. If too many detections, confidence might be too low", flush=True)
