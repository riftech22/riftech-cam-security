#!/usr/bin/env python3
"""Analisa snapshot yang ada untuk multi-kamera split."""

import sys

sys.stdout.reconfigure(line_buffering=True)

print("DEBUG: Script started!", flush=True)
sys.stdout.flush()

try:
    print("DEBUG: Importing modules...", flush=True)
    import cv2
    import numpy as np
    import os
    print("DEBUG: All imports successful!", flush=True)
except Exception as e:
    print(f"DEBUG: Import error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

def analyze_snapshot(snapshot_path):
    """Analisa snapshot untuk split frame dan detection."""
    
    print("=" * 70, flush=True)
    print(f"Analyzing Snapshot: {os.path.basename(snapshot_path)}", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)
    
    # Read snapshot
    frame = cv2.imread(snapshot_path)
    
    if frame is None:
        print(f"❌ Failed to read snapshot: {snapshot_path}", flush=True)
        return None
    
    h, w = frame.shape[:2]
    file_size = os.path.getsize(snapshot_path)
    
    print(f"[1/4] Snapshot Info:", flush=True)
    print(f"     Path: {snapshot_path}", flush=True)
    print(f"     Size: {file_size} bytes ({file_size/1024:.1f} KB)", flush=True)
    print(f"     Resolution: {w}x{h}", flush=True)
    print(f"     Mid point: {w//2}x{h//2}", flush=True)
    
    # Cek vertical split
    mid_y = h // 2
    top = frame[:mid_y, :]
    bottom = frame[mid_y:, :]
    
    print(f"\n[2/4] Split Analysis:", flush=True)
    print(f"     Top region: 0-{mid_y} (height: {mid_y})", flush=True)
    print(f"     Bottom region: {mid_y}-{h} (height: {h-mid_y})", flush=True)
    
    # Save split images
    output_base = f"split_{os.path.basename(snapshot_path).replace('.jpg', '')}"
    cv2.imwrite(f"{output_base}_full.jpg", frame)
    cv2.imwrite(f"{output_base}_top.jpg", top)
    cv2.imwrite(f"{output_base}_bottom.jpg", bottom)
    
    print(f"\n💾 Split images saved:", flush=True)
    print(f"     - {output_base}_full.jpg (full: {w}x{h})", flush=True)
    print(f"     - {output_base}_top.jpg (top: {w}x{mid_y})", flush=True)
    print(f"     - {output_base}_bottom.jpg (bottom: {w}x{h-mid_y})", flush=True)
    
    # Test YOLO detection
    print(f"\n[3/4] Testing YOLO Detection...", flush=True)
    
    try:
        from ultralytics import YOLO
        
        print(f"     Loading YOLO model...", flush=True)
        model = YOLO('yolov8n.pt')
        print(f"     ✅ Model loaded successfully", flush=True)
        
        # Resize untuk YOLO (optimal: 640x640)
        print(f"\n     Resizing for YOLO detection...", flush=True)
        top_resized = cv2.resize(top, (640, 480))
        bottom_resized = cv2.resize(bottom, (640, 480))
        
        # Detect top camera
        print(f"     📷 Detecting in TOP camera...", flush=True)
        results_top = model(top_resized, conf=0.25, classes=[0], verbose=False)
        persons_top = len(results_top[0].boxes)
        print(f"     ✅ Top camera: {persons_top} person(s) detected", flush=True)
        
        # Detect bottom camera
        print(f"     📷 Detecting in BOTTOM camera...", flush=True)
        results_bottom = model(bottom_resized, conf=0.25, classes=[0], verbose=False)
        persons_bottom = len(results_bottom[0].boxes)
        print(f"     ✅ Bottom camera: {persons_bottom} person(s) detected", flush=True)
        
        print(f"\n     📊 Total persons detected: {persons_top + persons_bottom}", flush=True)
        
        # Scale bounding boxes back to original size
        scale_x = w / 640
        scale_y = mid_y / 480
        
        # Draw detections on original top
        if persons_top > 0:
            for box in results_top[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                # Scale back
                x1_orig = int(x1 * scale_x)
                y1_orig = int(y1 * scale_y)
                x2_orig = int(x2 * scale_x)
                y2_orig = int(y2 * scale_y)
                cv2.rectangle(top, (x1_orig, y1_orig), (x2_orig, y2_orig), (0, 255, 0), 2)
                cv2.putText(top, f"{conf:.0%}", (x1_orig, y1_orig-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                print(f"     Top person: ({x1_orig}, {y1_orig}) -> ({x2_orig}, {y2_orig}) conf={conf:.2f}", flush=True)
        
        # Draw detections on original bottom
        scale_x_bottom = w / 640
        scale_y_bottom = (h - mid_y) / 480
        
        if persons_bottom > 0:
            for box in results_bottom[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                # Scale back
                x1_orig = int(x1 * scale_x_bottom)
                y1_orig = int(y1 * scale_y_bottom)
                x2_orig = int(x2 * scale_x_bottom)
                y2_orig = int(y2 * scale_y_bottom)
                cv2.rectangle(bottom, (x1_orig, y1_orig), (x2_orig, y2_orig), (0, 255, 0), 2)
                cv2.putText(bottom, f"{conf:.0%}", (x1_orig, y1_orig-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                print(f"     Bottom person: ({x1_orig}, {y1_orig}) -> ({x2_orig}, {y2_orig}) conf={conf:.2f}", flush=True)
        
        # Save detection results
        cv2.imwrite(f"{output_base}_top_detected.jpg", top)
        cv2.imwrite(f"{output_base}_bottom_detected.jpg", bottom)
        
        print(f"\n     💾 Detection results saved:", flush=True)
        print(f"         - {output_base}_top_detected.jpg", flush=True)
        print(f"         - {output_base}_bottom_detected.jpg", flush=True)
        
        # Analisa
        print(f"\n[4/4] Analysis:", flush=True)
        print(f"     Top camera bounding boxes: {persons_top}", flush=True)
        print(f"     Bottom camera bounding boxes: {persons_bottom}", flush=True)
        
        if persons_top > 0 and persons_bottom > 0:
            print(f"     ✅ Both cameras detected!", flush=True)
            print(f"     💡 Both cameras are working", flush=True)
        elif persons_top > 0:
            print(f"     ⚠️  Only TOP camera detected", flush=True)
            print(f"     💡 Bottom camera might be empty or not detecting", flush=True)
        elif persons_bottom > 0:
            print(f"     ⚠️  Only BOTTOM camera detected", flush=True)
            print(f"     💡 Top camera might be empty or not detecting", flush=True)
        else:
            print(f"     ❌ No persons detected in either camera", flush=True)
            print(f"     💡 Possible reasons:", flush=True)
            print(f"        - Snapshot taken when no one was present", flush=True)
            print(f"        - Lighting conditions too poor", flush=True)
            print(f"        - YOLO confidence threshold too high", flush=True)
            print(f"        - Camera angles not suitable for detection", flush=True)
        
    except Exception as e:
        print(f"\n     ❌ YOLO test error: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        print("DEBUG: Starting main function...", flush=True)
        sys.stdout.flush()
        
        # Check arguments
        if len(sys.argv) > 1:
            snapshot_path = sys.argv[1]
        else:
            # Use latest snapshot
            snapshot_dir = "snapshots"
            if not os.path.exists(snapshot_dir):
                print(f"❌ Snapshots directory not found: {snapshot_dir}", flush=True)
                sys.exit(1)
            
            snapshots = [f for f in os.listdir(snapshot_dir) if f.endswith('.jpg')]
            if not snapshots:
                print(f"❌ No snapshots found in {snapshot_dir}", flush=True)
                sys.exit(1)
            
            latest_snapshot = sorted(snapshots)[-1]
            snapshot_path = os.path.join(snapshot_dir, latest_snapshot)
        
        analyze_snapshot(snapshot_path)
        
        print()
        print("=" * 70, flush=True)
        print("✅ Analysis Complete!", flush=True)
        print("=" * 70, flush=True)
        print()
        print("📋 Next steps:", flush=True)
        print("   1. Check split images: split_*.jpg", flush=True)
        print("   2. Check detection results: split_*_detected.jpg", flush=True)
        print("   3. Send results to developer", flush=True)
        print(flush=True)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user", flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
