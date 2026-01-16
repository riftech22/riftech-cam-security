#!/usr/bin/env python3
"""Test MediaPipe 0.10.31 API structure."""

print("=" * 60)
print("  TEST MEDIAPIPE API STRUCTURE")
print("=" * 60)

# Test 1: Import mediapipe
print("\n1. Testing: import mediapipe as mp")
try:
    import mediapipe as mp
    print(f"✅ Success! MediaPipe version: {mp.__version__}")
except Exception as e:
    print(f"❌ Failed: {e}")
    exit(1)

# Test 2: Check mp.solutions (old API)
print("\n2. Testing: hasattr(mp, 'solutions')")
if hasattr(mp, 'solutions'):
    print("✅ mp.solutions exists!")
    print(f"   Type: {type(mp.solutions)}")
else:
    print("❌ mp.solutions NOT exists")

# Test 3: Try mp.solutions.Pose (old API)
print("\n3. Testing: mp.solutions.Pose")
try:
    pose = mp.solutions.Pose
    print(f"✅ Success! Type: {pose}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 4: Try from mediapipe.python.solutions (new API)
print("\n4. Testing: from mediapipe.python.solutions import pose")
try:
    from mediapipe.python.solutions import pose as mp_pose
    print(f"✅ Success! Type: {mp_pose}")
    print(f"   Has Pose class: {hasattr(mp_pose, 'Pose')}")
except Exception as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")

# Test 5: Try direct mediapipe.solutions
print("\n5. Testing: from mediapipe import solutions")
try:
    from mediapipe import solutions
    print(f"✅ Success! Type: {solutions}")
    print(f"   Has Pose class: {hasattr(solutions, 'Pose')}")
except Exception as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")

# Test 6: Try mediapipe.tasks.vision
print("\n6. Testing: from mediapipe.tasks import vision")
try:
    from mediapipe.tasks import vision
    print(f"✅ Success! Type: {vision}")
except Exception as e:
    print(f"❌ Failed: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("  TEST COMPLETE")
print("=" * 60)
