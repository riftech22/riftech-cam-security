#!/usr/bin/env python3
"""Check if RTSP stream is sending split frame or 2 separate streams."""

import cv2
import numpy as np
import time

print("=" * 70, flush=True)
print("Check RTSP Stream Split Configuration", flush=True)
print("=" * 70, flush=True)
print()

# RTSP URL
RTSP_URL = "rtsp://admin:Kuncong203@10.26.27.196:554/"

print(f"Connecting to RTSP: {RTSP_URL}", flush=True)
print("Capturing 3 frames for analysis...", flush=True)
print()

# Open RTSP
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("❌ Failed to open RTSP stream!", flush=True)
    print("Trying with FFmpeg...", flush=True)
    
    import subprocess
    
    # Try different RTSP paths
    rtsp_paths = [
        RTSP_URL,
        "rtsp://admin:Kuncong203@10.26.27.196:554/stream",
        "rtsp://admin:Kuncong203@10.26.27.196:554/live",
        "rtsp://admin:Kuncong203@10.26.27.196:554/1",
        "rtsp://admin:Kuncong203@10.26.27.196:554/2",
    ]
    
    for rtsp_path in rtsp_paths:
        print(f"\nTrying: {rtsp_path}", flush=True)
        
        ffmpeg_cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', rtsp_path,
            '-t', '1',
            '-f', 'image2',
            '-vframes', '3',
            'rtsp_check_%d.jpg'
        ]
        
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ SUCCESS! Captured 3 frames from {rtsp_path}", flush=True)
                
                # Check frame dimensions
                for i in range(1, 4):
                    frame_path = f'rtsp_check_{i}.jpg'
                    try:
                        frame = cv2.imread(frame_path)
                        if frame is not None:
                            h, w = frame.shape[:2]
                            print(f"\n   Frame {i}: {w}x{h}", flush=True)
                            
                            # Analyze frame content
                            top_half = frame[:h//2, :]
                            bottom_half = frame[h//2:, :]
                            
                            # Calculate average brightness
                            top_brightness = np.mean(top_half)
                            bottom_brightness = np.mean(bottom_half)
                            
                            print(f"   Top half brightness: {top_brightness:.2f}", flush=True)
                            print(f"   Bottom half brightness: {bottom_brightness:.2f}", flush=True)
                            
                            # Check if both halves have content
                            top_std = np.std(top_half)
                            bottom_std = np.std(bottom_half)
                            
                            print(f"   Top half std dev: {top_std:.2f}", flush=True)
                            print(f"   Bottom half std dev: {bottom_std:.2f}", flush=True)
                            
                            if top_std > 10 and bottom_std > 10:
                                print(f"   ✅ Both halves have content (SPLIT FRAME!)", flush=True)
                            else:
                                print(f"   ⚠️  One half might be empty", flush=True)
                    except Exception as e:
                        print(f"   ❌ Error reading frame {i}: {e}", flush=True)
                
                break
            else:
                print(f"❌ Failed: {result.stderr[:200]}", flush=True)
        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
    
    exit(1)

else:
    print("✅ RTSP opened with cv2.VideoCapture!", flush=True)
    
    # Capture 3 frames
    frames = []
    for i in range(3):
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
            h, w = frame.shape[:2]
            print(f"Frame {i+1}/3: {w}x{h}", flush=True)
        else:
            print(f"Failed to read frame {i+1}", flush=True)
        time.sleep(0.5)
    
    cap.release()
    
    if not frames:
        print("❌ No frames captured!", flush=True)
        exit(1)
    
    # Analyze middle frame
    frame = frames[len(frames)//2]
    h, w = frame.shape[:2]
    
    print()
    print("=" * 70, flush=True)
    print("FRAME ANALYSIS", flush=True)
    print("=" * 70, flush=True)
    print(f"Resolution: {w}x{h}", flush=True)
    print()
    
    # Split frame
    top_half = frame[:h//2, :]
    bottom_half = frame[h//2:, :]
    
    # Save split halves
    cv2.imwrite('rtsp_top_half.jpg', top_half)
    cv2.imwrite('rtsp_bottom_half.jpg', bottom_half)
    print(f"📸 Top half saved: rtsp_top_half.jpg", flush=True)
    print(f"📸 Bottom half saved: rtsp_bottom_half.jpg", flush=True)
    print()
    
    # Calculate statistics
    top_brightness = np.mean(top_half)
    bottom_brightness = np.mean(bottom_half)
    top_std = np.std(top_half)
    bottom_std = np.std(bottom_half)
    
    print("Brightness Analysis:", flush=True)
    print(f"  Top half: {top_brightness:.2f}", flush=True)
    print(f"  Bottom half: {bottom_brightness:.2f}", flush=True)
    print()
    
    print("Standard Deviation (content indicator):", flush=True)
    print(f"  Top half: {top_std:.2f}", flush=True)
    print(f"  Bottom half: {bottom_std:.2f}", flush=True)
    print()
    
    # Conclusion
    print("=" * 70, flush=True)
    print("CONCLUSION", flush=True)
    print("=" * 70, flush=True)
    
    if top_std > 10 and bottom_std > 10:
        print("✅ SPLIT FRAME DETECTED!", flush=True)
        print("   Both halves have content (camera is sending 2-in-1 frame)", flush=True)
        print()
        print("💡 SOLUTION:", flush=True)
        print("   Detect separately in top and bottom halves", flush=True)
        print("   Top: 0-360, Bottom: 360-720", flush=True)
    elif top_std > 10 and bottom_std < 10:
        print("⚠️  ONLY TOP HALF HAS CONTENT!", flush=True)
        print("   Bottom half is empty/black", flush=True)
        print()
        print("💡 SOLUTION:", flush=True)
        print("   Only detect in top half (0-360)", flush=True)
    elif top_std < 10 and bottom_std > 10:
        print("⚠️  ONLY BOTTOM HALF HAS CONTENT!", flush=True)
        print("   Top half is empty/black", flush=True)
        print()
        print("💡 SOLUTION:", flush=True)
        print("   Only detect in bottom half (360-720)", flush=True)
    else:
        print("❌ BOTH HALVES ARE EMPTY!", flush=True)
        print("   Frame might be black or corrupted", flush=True)
        print()
        print("💡 SOLUTION:", flush=True)
        print("   Check RTSP stream connection", flush=True)
    
    print()
    print("📸 Check the saved images:", flush=True)
    print("   - rtsp_top_half.jpg (top camera view)", flush=True)
    print("   - rtsp_bottom_half.jpg (bottom camera view)", flush=True)
