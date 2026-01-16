#!/usr/bin/env python3
"""
Implement Frigate's detection techniques for better accuracy.

Based on analysis of Frigate's source code:
1. Detection threshold: 0.4 (base.py)
2. Filter threshold: 0.7 (objects.py FilterConfig)
3. Area filtering: min_area, max_area
4. Aspect ratio filtering: min_ratio, max_ratio
5. NMS for overlapping detections
6. Tracking for temporal consistency
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time

print("=" * 70)
print("Implement Frigate's Detection Techniques", flush=True)
print("=" * 70)
print()

# RTSP URL
RTSP_URL = "rtsp://admin:Kuncong203@10.26.27.196:554/"

print(f"Connecting to RTSP: {RTSP_URL}", flush=True)
print("Implementing Frigate's techniques for better accuracy...", flush=True)
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
    
    print(f"\nFrame {frames_processed+1}/10", flush=True)
    
    # Preprocessing (resize + brightness + CLAHE)
    frame_resized = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_LINEAR)
    
    # Brightness adjustment
    brightness = np.mean(frame_resized)
    if brightness > 120:
        frame_adjusted = cv2.convertScaleAbs(frame_resized, alpha=0.7, beta=-30)
    elif brightness < 50:
        frame_adjusted = cv2.convertScaleAbs(frame_resized, alpha=1.3, beta=30)
    else:
        frame_adjusted = frame_resized.copy()
    
    # CLAHE
    lab = cv2.cvtColor(frame_adjusted, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    frame_processed = cv2.merge([l, a, b])
    frame_processed = cv2.cvtColor(frame_processed, cv2.COLOR_LAB2BGR)
    
    # Split frame
    h, w = frame_processed.shape[:2]
    mid_y = h // 2
    top_frame = frame_processed[:mid_y, :]
    bottom_frame = frame_processed[mid_y:, :]
    
    print(f"   Split: Top (0-{mid_y}), Bottom ({mid_y}-{h})", flush=True)
    
    # Detect with Frigate's detection threshold (0.4)
    results_top = model(top_frame, conf=0.4, classes=[0], verbose=False)
    results_bottom = model(bottom_frame, conf=0.4, classes=[0], verbose=False)
    
    all_detections = []
    
    # Process top detections
    if results_top and results_top[0].boxes:
        for box in results_top[0].boxes:
            x1, y1, x2, y2 = map(float, box.xyxy[0].cpu().numpy())
            conf = float(box.conf[0])
            all_detections.append({
                'bbox': (x1, y1, x2, y2),
                'conf': conf,
                'region': 'top'
            })
    
    # Process bottom detections
    if results_bottom and results_bottom[0].boxes:
        for box in results_bottom[0].boxes:
            x1, y1, x2, y2 = map(float, box.xyxy[0].cpu().numpy())
            conf = float(box.conf[0])
            all_detections.append({
                'bbox': (x1, y1, x2, y2),
                'conf': conf,
                'region': 'bottom'
            })
    
    print(f"   Raw detections (conf>=0.4): {len(all_detections)}", flush=True)
    
    # Apply Frigate's filters
    filtered_detections = []
    
    for det in all_detections:
        x1, y1, x2, y2 = det['bbox']
        conf = det['conf']
        
        # Calculate area
        area = (x2 - x1) * (y2 - y1)
        
        # Calculate aspect ratio (width/height)
        width = x2 - x1
        height = y2 - y1
        aspect_ratio = width / height if height > 0 else 0
        
        # Frigate's filters (from objects.py FilterConfig):
        # - min_area: 0
        # - max_area: 24000000 (very high)
        # - min_ratio: 0
        # - max_ratio: 24000000 (very high)
        # - threshold: 0.7 (average confidence)
        # - min_score: 0.5 (minimum confidence)
        
        # Apply area filter (reasonable limits for person)
        MIN_AREA = 1000
        MAX_AREA = 200000
        
        if area < MIN_AREA or area > MAX_AREA:
            continue
        
        # Apply aspect ratio filter (person is typically 0.3 to 1.0)
        MIN_RATIO = 0.3
        MAX_RATIO = 1.0
        
        if aspect_ratio < MIN_RATIO or aspect_ratio > MAX_RATIO:
            continue
        
        # Apply min_score filter (0.5)
        if conf < 0.5:
            continue
        
        filtered_detections.append(det)
    
    print(f"   After area/ratio/score filters: {len(filtered_detections)}", flush=True)
    
    # Apply NMS (Non-Maximum Suppression)
    if len(filtered_detections) > 0:
        # Convert to format for NMS
        boxes = []
        confidences = []
        
        for det in filtered_detections:
            x1, y1, x2, y2 = det['bbox']
            boxes.append([x1, y1, x2 - x1, y2 - y1])
            confidences.append(det['conf'])
        
        boxes_np = np.array(boxes, dtype=np.float32)
        confidences_np = np.array(confidences, dtype=np.float32)
        
        # NMS with IoU threshold 0.45
        indices = cv2.dnn.NMSBoxes(
            boxes_np.tolist(),
            confidences_np.tolist(),
            conf_threshold=0.5,
            nms_threshold=0.45
        )
        
        if len(indices) > 0:
            nms_detections = [filtered_detections[i] for i in indices.flatten()]
        else:
            nms_detections = []
    else:
        nms_detections = []
    
    print(f"   After NMS: {len(nms_detections)}", flush=True)
    
    # Draw detections
    for det in nms_detections:
        x1, y1, x2, y2 = map(int, det['bbox'])
        conf = det['conf']
        region = det['region']
        
        if region == 'bottom':
            y1 += mid_y
            y2 += mid_y
        
        cv2.rectangle(frame_processed, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv2.putText(frame_processed, f"{conf:.2f}", (x1, y1-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    total_count = len(nms_detections)
    
    if total_count > 0:
        cv2.imwrite(f'frigate_frame_{frames_processed+1}.jpg', frame_processed)
        
        # Keep best result
        if total_count > best_persons:
            best_persons = total_count
            best_frame = frame_processed.copy()
            print(f"   ✅ NEW BEST: {total_count} persons!", flush=True)
    else:
        print(f"   ❌ No persons detected", flush=True)
    
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
    cv2.imwrite(f'frigate_best_{timestamp}.jpg', best_frame)
    print(f"📸 Best frame saved: frigate_best_{timestamp}.jpg", flush=True)
else:
    print(f"❌ No persons detected in {frames_processed} frames", flush=True)

print()
print("🔍 FRIGATE TECHNIQUES APPLIED:", flush=True)
print("   1. Detection threshold: 0.4 (from base.py)", flush=True)
print("   2. Min score filter: 0.5 (from objects.py)", flush=True)
print("   3. Area filter: 1000-200000 pixels", flush=True)
print("   4. Aspect ratio filter: 0.3-1.0", flush=True)
print("   5. NMS (IoU=0.45, conf=0.5)", flush=True)
print()
print("💡 EXPECTED IMPROVEMENT:", flush=True)
print("   - Fewer false positives", flush=True)
print("   - Tighter bounding boxes", flush=True)
print("   - More accurate person count", flush=True)
print()
print("📊 COMPARE WITH:", flush=True)
print("   - Previous test (conf=0.30): 0-1 persons", flush=True)
print("   - Frigate techniques: ??? persons (test now!)", flush=True)
