"""
Test emotion detection with realistic synthetic faces
"""

import cv2
import numpy as np
from emotion_detector import EmotionDetector
from pathlib import Path

print("=" * 60)
print("Emotion Detection System - Feature-Based Test")
print("=" * 60)

# Initialize detector
print("\n▶ Initializing Emotion Detector...")
detector = EmotionDetector()
print("✓ Emotion Detector initialized")

# Create output directory
Path("output").mkdir(exist_ok=True)

# Function to create realistic synthetic faces
def create_synthetic_face(image_size=256, emotion_type='neutral'):
    """Create a synthetic face with emotion-specific features"""
    img = np.ones((image_size, image_size, 3), dtype=np.uint8) * 200
    center = image_size // 2
    
    if emotion_type == 'happy':
        # Bright, saturated colors, big smile
        img = np.ones((image_size, image_size, 3), dtype=np.uint8) * 240
        # Face color - bright peachy
        cv2.circle(img, (center, center), 80, (100, 150, 255), -1)  # BGR: peachy
        # Eyes - bright
        cv2.circle(img, (center - 30, center - 20), 12, (255, 255, 255), -1)
        cv2.circle(img, (center + 30, center - 20), 12, (255, 255, 255), -1)
        cv2.circle(img, (center - 30, center - 20), 6, (0, 100, 200), -1)
        cv2.circle(img, (center + 30, center - 20), 6, (0, 100, 200), -1)
        # Big smile
        cv2.ellipse(img, (center, center + 30), (45, 25), 0, 0, 180, (100, 100, 200), 3)
        cv2.ellipse(img, (center, center + 32), (40, 20), 0, 0, 180, (150, 100, 150), -1)
        # Rosy cheeks
        cv2.circle(img, (center - 50, center), 20, (120, 180, 255), -1)
        cv2.circle(img, (center + 50, center), 20, (120, 180, 255), -1)
        
    elif emotion_type == 'sad':
        # Dark, desaturated, downturned mouth
        img = np.ones((image_size, image_size, 3), dtype=np.uint8) * 180
        # Face color - grayish
        cv2.circle(img, (center, center), 80, (120, 120, 120), -1)
        # Eyes - tired, droopy
        cv2.ellipse(img, (center - 30, center - 20), (12, 10), 0, 0, 360, (200, 200, 200), -1)
        cv2.ellipse(img, (center + 30, center - 20), (12, 10), 0, 0, 360, (200, 200, 200), -1)
        cv2.circle(img, (center - 30, center - 18), 5, (50, 50, 50), -1)
        cv2.circle(img, (center + 30, center - 18), 5, (50, 50, 50), -1)
        # Sad mouth (downturned)
        cv2.ellipse(img, (center, center + 35), (35, 20), 0, 180, 360, (100, 100, 100), 3)
        cv2.line(img, (center - 35, center + 30), (center, center + 40), (100, 100, 100), 2)
        cv2.line(img, (center + 35, center + 30), (center, center + 40), (100, 100, 100), 2)
        
    elif emotion_type == 'angry':
        # High contrast, furrowed brow
        img = np.ones((image_size, image_size, 3), dtype=np.uint8) * 160
        # Face color - reddish
        cv2.circle(img, (center, center), 80, (80, 100, 180), -1)
        # Angry eyes - narrow, furrowed brow
        cv2.ellipse(img, (center - 30, center - 25), (15, 8), -20, 0, 360, (150, 150, 150), -1)
        cv2.ellipse(img, (center + 30, center - 25), (15, 8), 20, 0, 360, (150, 150, 150), -1)
        cv2.circle(img, (center - 30, center - 25), 4, (0, 0, 0), -1)
        cv2.circle(img, (center + 30, center - 25), 4, (0, 0, 0), -1)
        # Furrowed brow
        cv2.line(img, (center - 40, center - 40), (center - 20, center - 35), (100, 100, 100), 3)
        cv2.line(img, (center + 40, center - 40), (center + 20, center - 35), (100, 100, 100), 3)
        # Frown/tense mouth
        cv2.ellipse(img, (center, center + 35), (30, 15), 0, 180, 360, (80, 80, 120), -1)
        cv2.line(img, (center, center + 25), (center, center + 40), (80, 80, 120), 2)
        
    elif emotion_type == 'surprised':
        # Very bright, high saturation, big eyes, O mouth
        img = np.ones((image_size, image_size, 3), dtype=np.uint8) * 245
        # Face color - very bright peachy
        cv2.circle(img, (center, center), 80, (120, 180, 255), -1)
        # Very wide eyes
        cv2.ellipse(img, (center - 30, center - 20), (16, 18), 0, 0, 360, (255, 255, 255), -1)
        cv2.ellipse(img, (center + 30, center - 20), (16, 18), 0, 0, 360, (255, 255, 255), -1)
        cv2.circle(img, (center - 30, center - 20), 8, (0, 100, 200), -1)
        cv2.circle(img, (center + 30, center - 20), 8, (0, 100, 200), -1)
        cv2.circle(img, (center - 30, center - 20), 4, (0, 0, 0), -1)
        cv2.circle(img, (center + 30, center - 20), 4, (0, 0, 0), -1)
        # O-shaped mouth
        cv2.circle(img, (center, center + 40), 18, (100, 80, 180), -1)
        cv2.circle(img, (center, center + 40), 12, (200, 100, 100), -1)
        
    elif emotion_type == 'fear':
        # Mixed brightness, raised eyebrows, open mouth
        img = np.ones((image_size, image_size, 3), dtype=np.uint8) * 210
        # Face color - pale
        cv2.circle(img, (center, center), 80, (160, 150, 180), -1)
        # Wide, fearful eyes
        cv2.ellipse(img, (center - 30, center - 25), (14, 16), 0, 0, 360, (255, 255, 255), -1)
        cv2.ellipse(img, (center + 30, center - 25), (14, 16), 0, 0, 360, (255, 255, 255), -1)
        cv2.circle(img, (center - 30, center - 25), 7, (0, 100, 200), -1)
        cv2.circle(img, (center + 30, center - 25), 7, (0, 100, 200), -1)
        # Raised eyebrows
        cv2.ellipse(img, (center - 35, center - 45), (18, 8), -15, 0, 360, (140, 140, 140), -1)
        cv2.ellipse(img, (center + 35, center - 45), (18, 8), 15, 0, 360, (140, 140, 140), -1)
        # Open mouth (fearful)
        cv2.ellipse(img, (center, center + 35), (25, 30), 0, 0, 180, (100, 80, 150), -1)
        
    elif emotion_type == 'disgust':
        # Very low saturation, wrinkled nose, asymmetric mouth
        img = np.ones((image_size, image_size, 3), dtype=np.uint8) * 170
        # Face color - very desaturated, grayish-green
        cv2.circle(img, (center, center), 80, (140, 130, 130), -1)
        # Eyes - narrowed, skeptical
        cv2.ellipse(img, (center - 30, center - 20), (12, 8), 0, 0, 360, (180, 180, 180), -1)
        cv2.ellipse(img, (center + 30, center - 20), (12, 8), 0, 0, 360, (180, 180, 180), -1)
        cv2.circle(img, (center - 30, center - 20), 4, (50, 50, 50), -1)
        cv2.circle(img, (center + 30, center - 20), 4, (50, 50, 50), -1)
        # Wrinkled nose
        cv2.line(img, (center - 15, center - 5), (center - 15, center + 15), (100, 100, 100), 2)
        cv2.line(img, (center + 15, center - 5), (center + 15, center + 15), (100, 100, 100), 2)
        cv2.line(img, (center, center - 2), (center, center + 10), (100, 100, 100), 2)
        # Asymmetric mouth
        cv2.line(img, (center - 30, center + 35), (center, center + 30), (80, 80, 80), 3)
        cv2.line(img, (center, center + 30), (center + 35, center + 40), (80, 80, 80), 3)
        
    else:  # neutral
        # Balanced features
        img = np.ones((image_size, image_size, 3), dtype=np.uint8) * 220
        # Face color - natural
        cv2.circle(img, (center, center), 80, (130, 150, 200), -1)
        # Normal eyes
        cv2.circle(img, (center - 30, center - 20), 12, (220, 220, 220), -1)
        cv2.circle(img, (center + 30, center - 20), 12, (220, 220, 220), -1)
        cv2.circle(img, (center - 30, center - 20), 6, (0, 100, 200), -1)
        cv2.circle(img, (center + 30, center - 20), 6, (0, 100, 200), -1)
        # Neutral mouth (straight line)
        cv2.line(img, (center - 30, center + 35), (center + 30, center + 35), (100, 100, 100), 2)
    
    return img

# Create test images
print("\n▶ Creating test face images with emotion-specific features...")
test_cases = [
    ('happy', 'Bright, saturated face (Happy)'),
    ('sad', 'Dark, desaturated face (Sad)'),
    ('angry', 'High contrast face (Angry)'),
    ('surprised', 'Very bright, big eyes (Surprised)'),
    ('fear', 'Mixed brightness, raised eyebrows (Fear)'),
    ('disgust', 'Desaturated, wrinkled nose (Disgust)'),
    ('neutral', 'Balanced face (Neutral)'),
]

results = {}
for emotion_type, description in test_cases:
    print(f"\n✓ Test: {description}")
    test_image = create_synthetic_face(256, emotion_type)
    
    # Detect emotion
    emotion_dict = detector.detect_emotion(test_image)
    dominant_emotion, confidence = detector.get_dominant_emotion(emotion_dict)
    
    results[emotion_type] = (dominant_emotion, confidence)
    
    # Print results
    print(f"  Dominant Emotion: {dominant_emotion.upper()} ({confidence:.1%})")
    print(f"  All Emotions:")
    
    for emo, prob in sorted(emotion_dict.items(), key=lambda x: x[1], reverse=True):
        bar_length = int(prob * 30)
        bar = "█" * bar_length
        print(f"    {emo:12} | {bar} {prob:.1%}")
    
    # Save test image
    cv2.imwrite(f"output/emotion_test_{emotion_type}.jpg", test_image)

print("\n" + "=" * 60)
print("Emotion Detection Summary")
print("=" * 60)

correct = 0
for emotion_type, (detected, confidence) in results.items():
    status = "✓" if detected == emotion_type else "~"
    if detected == emotion_type:
        correct += 1
    print(f"{status} {emotion_type:12} -> Detected: {detected:12} ({confidence:.1%})")

accuracy = correct / len(results)
print(f"\nAccuracy: {accuracy:.0%} ({correct}/{len(results)})")

print("\n" + "=" * 60)
print("✓ Emotion Detection Test Completed!")
print("=" * 60)
print("\nKey Features of Emotion Detection:")
print("  • Analyzes brightness, saturation, contrast")
print("  • Detects edge density and texture variance")
print("  • Analyzes facial regions (eyes, nose, mouth)")
print("  • Combines features for emotion probability")
print("  • Shows all 7 emotion probabilities")
print("  • Real-time feature-based detection")
print("\nTest images saved in: output/emotion_test_*.jpg")
print("Run 'python main.py' to see live emotion detection!")
