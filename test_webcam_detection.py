"""
Test face detection with real webcam feed
"""

import cv2
import sys
from face_detector import FaceDetector
from pathlib import Path

print("=" * 60)
print("Webcam Face Detection Test")
print("=" * 60)

# Initialize detector
print("\n▶ Initializing Face Detector...")
detector = FaceDetector(confidence_threshold=0.5)
print("✓ Face Detector initialized")

# Try to capture from webcam
print("\n▶ Opening webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Failed to open webcam")
    print("   Please check if camera is connected and accessible")
    sys.exit(1)

print("✓ Webcam opened successfully")

# Capture a single frame
print("\n▶ Capturing frame from webcam...")
ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ Failed to capture frame")
    sys.exit(1)

print(f"✓ Frame captured: {frame.shape}")

# Save original frame
cv2.imwrite("webcam_frame_original.jpg", frame)
print("  Saved: webcam_frame_original.jpg")

# Detect faces
print("\n▶ Running face detection...")
detections = detector.detect_faces(frame)

print(f"\n✓ Detection Results:")
print(f"  - Total faces detected: {len(detections)}")

if len(detections) > 0:
    for i, det in enumerate(detections):
        x_min, y_min, x_max, y_max = det['bbox']
        width = x_max - x_min
        height = y_max - y_min
        confidence = det['confidence']
        print(f"\n  Face {i+1}:")
        print(f"    - Position: ({x_min}, {y_min}) to ({x_max}, {y_max})")
        print(f"    - Size: {width}x{height}")
        print(f"    - Confidence: {confidence:.2%}")
else:
    print("  ⚠ No faces detected in frame")
    print("\n  Troubleshooting:")
    print("  1. Make sure your face is clearly visible in the camera")
    print("  2. Ensure adequate lighting")
    print("  3. Position face directly facing the camera")
    print("  4. Try getting closer or farther from camera")

# Draw detections
result = detector.draw_detections(frame, detections)
cv2.imwrite("webcam_frame_detections.jpg", result)
print(f"\n  Saved: webcam_frame_detections.jpg")

# Display frame info
h, w = frame.shape[:2]
print(f"\n▶ Frame Information:")
print(f"  - Resolution: {w}x{h}")
print(f"  - Cascade Classifier: {detector.face_cascade.empty()}")

print("\n" + "=" * 60)
if len(detections) > 0:
    print("✓ Face detection working!")
else:
    print("⚠ No faces detected. Check lighting and camera positioning.")
print("=" * 60)
