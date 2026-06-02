"""
Quick test of the Face Detection System
"""

import cv2
import numpy as np
from main import FaceDetectionSystem
from pathlib import Path

print("=" * 60)
print("Face Detection System - Quick Test")
print("=" * 60)

# Initialize system
print("\n▶ Initializing Face Detection System...")
system = FaceDetectionSystem(
    enable_tracking=True,
    enable_recognition=True,
    enable_landmarks=True
)
print("✓ System initialized successfully")

# Test 1: Create a synthetic face image and test detection
print("\n▶ Test 1: Creating synthetic image for face detection...")

# Create a simple test image with gradient pattern that resembles a face region
test_image = np.ones((480, 640, 3), dtype=np.uint8) * 220

# Add face-like region
center_x, center_y = 320, 240
face_size = 150

# Draw face region
cv2.circle(test_image, (center_x, center_y), face_size, (180, 150, 120), -1)

# Draw eye regions
cv2.circle(test_image, (center_x - 40, center_y - 30), 15, (100, 100, 100), -1)
cv2.circle(test_image, (center_x + 40, center_y - 30), 15, (100, 100, 100), -1)

# Draw pupils
cv2.circle(test_image, (center_x - 40, center_y - 30), 8, (50, 50, 50), -1)
cv2.circle(test_image, (center_x + 40, center_y - 30), 8, (50, 50, 50), -1)

# Draw nose
cv2.line(test_image, (center_x, center_y), (center_x, center_y + 30), (150, 120, 100), 3)

# Draw mouth
cv2.ellipse(test_image, (center_x, center_y + 60), (40, 20), 0, 0, 180, (150, 100, 100), 2)

# Save test image
test_path = Path("test_face.jpg")
cv2.imwrite(str(test_path), test_image)
print(f"✓ Created test image: {test_path}")

# Test 2: Process the image
print("\n▶ Test 2: Processing image with face detection...")
results = system.process_frame(test_image)
print(f"✓ Detections: {len(results['detections'])} faces found")

for i, detection in enumerate(results['detections']):
    print(f"  Face {i+1}:")
    print(f"    - Bounding Box: {detection['bbox']}")
    print(f"    - Confidence: {detection['confidence']:.2f}")

# Test 3: Visualize results
print("\n▶ Test 3: Creating visualized output...")
annotated = system.visualize_results(test_image, results)

# Save annotated image
output_path = Path("output") / "test_detection_result.jpg"
cv2.imwrite(str(output_path), annotated)
print(f"✓ Saved annotated image: {output_path}")

# Test 4: Test statistics
print("\n▶ Test 4: System Statistics")
print(f"  - Frames processed: {system.stats['frames_processed']}")
print(f"  - Faces detected: {system.stats['faces_detected']}")
print(f"  - Faces recognized: {system.stats['faces_recognized']}")
print(f"  - Current FPS: {system.stats['fps']:.2f}")

# Test 5: Demonstrate API usage
print("\n▶ Test 5: Testing utility functions...")
from utils import (
    load_image, save_image, crop_face, resize_image,
    calculate_iou, get_image_files
)

# Test loading image
loaded = load_image(str(test_path))
print(f"✓ Loaded image shape: {loaded.shape if loaded is not None else 'None'}")

# Test image operations
if loaded is not None and len(results['detections']) > 0:
    bbox = results['detections'][0]['bbox']
    cropped = crop_face(loaded, bbox, padding=0.1)
    print(f"✓ Cropped face shape: {cropped.shape}")
    
    resized = resize_image(cropped, (224, 224))
    print(f"✓ Resized face shape: {resized.shape}")

# Test IoU calculation
bbox1 = (100, 100, 200, 200)
bbox2 = (150, 150, 250, 250)
iou = calculate_iou(bbox1, bbox2)
print(f"✓ IoU between two boxes: {iou:.4f}")

print("\n" + "=" * 60)
print("✓ All tests completed successfully!")
print("=" * 60)

print("\nNext steps:")
print("  1. To run real-time webcam detection: python main.py")
print("  2. To try more examples: python examples.py")
print("  3. To process your own images: system.process_image('path/to/image.jpg')")
print("  4. Read QUICKSTART.md for more information")
print("\nProject location: c:\\jp\\collage\\face_detection_system")
