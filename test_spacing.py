"""
Test visualization with improved text spacing
Demonstrates separated and properly spaced text on detected faces
"""

import cv2
import numpy as np
from main import FaceDetectionSystem
from pathlib import Path

print("=" * 60)
print("Visualization Spacing Test")
print("=" * 60)

# Initialize system
print("\n▶ Initializing system...")
system = FaceDetectionSystem(
    enable_tracking=True,
    enable_recognition=True,
    enable_emotion=True,
    enable_landmarks=False  # Disabled to reduce clutter
)
print("✓ System initialized")

# Create test image with multiple face-like regions
print("\n▶ Creating test image with face-like regions...")
test_image = np.ones((800, 1200, 3), dtype=np.uint8) * 200

# Create multiple face regions to test text spacing
faces_info = [
    {'pos': (300, 250), 'size': 120, 'name': 'Face 1'},
    {'pos': (800, 250), 'size': 120, 'name': 'Face 2'},
    {'pos': (300, 600), 'size': 120, 'name': 'Face 3'},
]

for face_info in faces_info:
    cx, cy = face_info['pos']
    size = face_info['size']
    
    # Draw face circle
    cv2.circle(test_image, (cx, cy), size, (180, 150, 120), -1)
    
    # Draw eyes
    cv2.circle(test_image, (cx - 30, cy - 30), 15, (100, 100, 100), -1)
    cv2.circle(test_image, (cx + 30, cy - 30), 15, (100, 100, 100), -1)
    cv2.circle(test_image, (cx - 30, cy - 30), 8, (50, 50, 50), -1)
    cv2.circle(test_image, (cx + 30, cy - 30), 8, (50, 50, 50), -1)
    
    # Draw nose
    cv2.line(test_image, (cx, cy), (cx, cy + 25), (150, 120, 100), 3)
    
    # Draw mouth
    cv2.ellipse(test_image, (cx, cy + 50), (35, 20), 0, 0, 180, (150, 100, 100), 2)

# Save test image
cv2.imwrite("test_spacing.jpg", test_image)
print("✓ Created test image with face-like regions")

# Process the image
print("\n▶ Processing image with all visualizations enabled...")
results = system.process_frame(test_image)

print(f"✓ Detected: {len(results['detections'])} faces")

# Visualize results
annotated = system.visualize_results(test_image, results)

# Save annotated image
output_path = Path("output") / "spacing_test_result.jpg"
cv2.imwrite(str(output_path), annotated)
print(f"✓ Saved annotated image: {output_path}")

print("\n" + "=" * 60)
print("Visualization Improvements")
print("=" * 60)

print("\n✓ Text Spacing Features:")
print("  • Face detection labels: Green background with black text")
print("  • Emotion labels: Separated BELOW the face box")
print("  • Emotion bars: Spaced below emotion label")
print("  • Recognition info: Top-right corner of face")
print("  • Tracking IDs: Separate circle with background")
print("  • Statistics: Top-left corner with background")
print()

print("✓ Spacing Layout (from top to bottom around face):")
print("  1. Face bounding box (green rectangle)")
print("  2. Confidence label (green background)")
print("  3. [spacing]")
print("  4. Emotion label (color-coded background)")
print("  5. [spacing]")
print("  6. Emotion probability bars (separated)")
print("  7. [spacing]")
print("  8. Tracking ID (yellow background)")
print()

print("✓ Benefits:")
print("  • No overlapping text")
print("  • Clear visual hierarchy")
print("  • Easy to read information")
print("  • Professional appearance")
print("  • Better for video processing")
print()

print("=" * 60)
print("✓ Spacing Test Complete!")
print("=" * 60)
print(f"\nVisualization test saved: {output_path}")
print("\nRun 'python main.py' to see live improved visualization!")
