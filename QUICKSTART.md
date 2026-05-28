# Quick Start Guide - Optimized Machine Learning Model for Accurate Face Detection in Real-Time Application

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Camera/webcam for real-time detection (optional)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Setup Script (Optional)
```bash
python setup.py
```

## Usage

### Option 1: Real-time Webcam Detection (Easiest)
```bash
python main.py
```
This will open your webcam and display:
- ✓ Detected faces with bounding boxes
- ✓ Facial landmarks (468 points)
- ✓ Emotions (angry, happy, sad, etc.)
- ✓ Face tracking IDs
- ✓ Real-time FPS counter

**Controls:**
- Press `q` to exit

### Option 2: Try Examples
```bash
python examples.py
```

Then select from:
1. Webcam Detection
2. Image Processing
3. Face Enrollment
4. Detection Analysis
5. Batch Processing
6. Video Processing
7. Face Tracking
8. Performance Benchmark

### Option 3: Python API

```python
from main import FaceDetectionSystem
import cv2

# Initialize system
system = FaceDetectionSystem()

# Process a single image
annotated = system.process_image("photo.jpg")

# Show result
cv2.imshow("Result", annotated)
cv2.waitKey(0)
```

## Features Overview

| Feature | Capability | Status |
|---------|-----------|--------|
| Face Detection | Multi-face, real-time | ✓ Ready |
| Landmarks | 468-point mesh | ✓ Ready |
| Emotion Recognition | 7 emotions | ✓ Ready |
| Face Recognition | Person identification | ✓ Ready |
| Face Tracking | Centroid tracking | ✓ Ready |
| Performance | 15-30 FPS (CPU) | ✓ Good |

## Configuration

Edit `config.py` to customize:

```python
# Detection confidence (0-1, higher = stricter)
FACE_DETECTION_CONFIG['confidence_threshold'] = 0.5

# Show/hide components
DISPLAY_CONFIG['show_landmarks'] = True
DISPLAY_CONFIG['show_emotion'] = True

# Camera resolution
VIDEO_CONFIG['frame_width'] = 1280
VIDEO_CONFIG['frame_height'] = 720
```

## Common Tasks

### Detect Faces in an Image
```python
from main import FaceDetectionSystem

system = FaceDetectionSystem()
result = system.process_image("image.jpg", save_output=True)
```

### Process Video File
```python
import cv2
from main import FaceDetectionSystem

system = FaceDetectionSystem()
cap = cv2.VideoCapture("video.mp4")

while True:
    ret, frame = cap.read()
    if not ret: break
    
    results = system.process_frame(frame)
    annotated = system.visualize_results(frame, results)
    
    cv2.imshow("Video", annotated)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Enroll Person for Recognition
```python
from main import FaceDetectionSystem

system = FaceDetectionSystem()

# Enroll with 3-5 photos
system.enroll_face("Alice", [
    "alice_1.jpg",
    "alice_2.jpg", 
    "alice_3.jpg"
])

# List enrolled people
people = system.face_recognizer.list_enrolled_people()
print(people)  # ['Alice']
```

### Process Image Directory
```python
from main import FaceDetectionSystem
from utils import get_image_files
from pathlib import Path

system = FaceDetectionSystem()
images = get_image_files("my_photos")

for img_path in images:
    result = system.process_image(img_path, save_output=True)
    print(f"Processed: {img_path}")
```

## Troubleshooting

### Slow Performance
**Solution:**
- Reduce resolution in `config.py`:
  ```python
  VIDEO_CONFIG['frame_width'] = 640
  VIDEO_CONFIG['frame_height'] = 480
  ```
- Use faster detection model:
  ```python
  FACE_DETECTION_CONFIG['model_selection'] = 0
  ```

### No Faces Detected
**Solution:**
- Check lighting conditions
- Ensure face is clearly visible
- Lower detection threshold:
  ```python
  FACE_DETECTION_CONFIG['confidence_threshold'] = 0.3
  ```

### Recognition Not Working
**Solution:**
- Enroll with better quality images
- Vary lighting and angles during enrollment
- Use 3-5 images per person (minimum)

### Camera Not Found
**Solution:**
- Check if camera is connected
- Try different camera ID:
  ```python
  system.run_webcam(camera_id=1)  # Try ID 1 instead of 0
  ```

## Output Files

The system creates:
- `output/` - Processed images with detections
- `logs/` - Application logs
- `face_database/` - Enrolled faces data
- `data/` - Working data directory

## Advanced Usage

### Access Raw Detection Data
```python
from main import FaceDetectionSystem

system = FaceDetectionSystem()
frame = cv2.imread("photo.jpg")

results = system.process_frame(frame)

# Access components
for i, detection in enumerate(results['detections']):
    print(f"Face {i}: confidence={detection['confidence']:.2f}")
    print(f"  BBox: {detection['bbox']}")

for i, emotion in enumerate(results['emotions']):
    print(f"Face {i} emotions: {emotion}")

for i, recognition in enumerate(results['recognitions']):
    print(f"Face {i}: {recognition['name']} ({recognition['confidence']:.2f})")
```

### Face Tracking
```python
# Get tracked face IDs
tracking = results['tracking']
for face_id, (x, y) in tracking.items():
    print(f"Face ID {face_id} at position ({x}, {y})")
    
    # Get motion vector
    motion = system.face_tracker.get_motion_vector(face_id)
    print(f"  Motion: {motion}")
```

## Performance Tips

1. **GPU Acceleration**: Install `tensorflow-gpu` for faster inference
2. **Batch Processing**: Process multiple images in parallel
3. **Skip Frames**: Use `skip_frames` in config to process every Nth frame
4. **Model Optimization**: Use quantized/pruned models for edge deployment

## Next Steps

1. ✓ Run `python main.py` to test with your webcam
2. Read `README.md` for complete documentation
3. Explore `examples.py` for advanced usage
4. Check `config.py` for customization options

## Support

- Documentation: See `README.md`
- Examples: Run `python examples.py`
- Issues: Check this guide's troubleshooting section

---

**Ready to detect faces? Run: `python main.py`** 🎥
