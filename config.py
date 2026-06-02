"""
Configuration file for Face Detection System
"""

import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Create directories
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Face Detection Settings
FACE_DETECTION_CONFIG = {
    'confidence_threshold': 0.5,
    'model_selection': 1,  # 1 for better accuracy, 0 for speed
}

# Facial Landmarks Settings
LANDMARKS_CONFIG = {
    'static_mode': False,
    'max_num_faces': 10,
    'refine_landmarks': True,
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
}

# Face Recognition Settings
RECOGNITION_CONFIG = {
    'model_type': 'vggface2',  # 'vggface2' or 'openface'
    'distance_threshold': 0.6,
}

# Face Tracking Settings
TRACKING_CONFIG = {
    'max_disappeared': 50,
    'max_distance': 100,
    'tracker_type': 'centroid',  # 'centroid' or 'kalman'
}

# Video Settings
VIDEO_CONFIG = {
    'camera_id': 0,
    'fps': 30,
    'frame_width': 1280,
    'frame_height': 720,
    'skip_frames': 0,  # Process every Nth frame
}

# Display Settings
DISPLAY_CONFIG = {
    'show_face_detection': True,
    'show_landmarks': True,
    'show_recognition': True,
    'show_tracking': True,
    'show_emotions': True,
    'draw_contour': True,
    'font_size': 0.9,
    'line_width': 2,
}

# Output Settings
OUTPUT_CONFIG = {
    'save_video': False,
    'save_frames': False,
    'save_detections': True,
    'output_format': 'mp4',
    'video_codec': 'mp4v',
    'fps': 30,
}

# Logging Settings
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_file': PROJECT_ROOT / 'logs' / 'face_detection.log',
    'save_logs': True,
}

# Advanced Settings
ADVANCED_CONFIG = {
    'use_gpu': True,
    'max_workers': 4,
    'batch_size': 4,
    'augmentation': True,
    'use_padding': True,
}

# Emotion Detection Settings
EMOTION_CONFIG = {
    'input_size': 128,
    'use_clahe': True,
    'clahe_clip_limit': 2.0,
    'clahe_grid_size': (8, 8),
    'gamma': 1.1,
    'smoothing_alpha': 0.6,
    'history_max_idle': 30,
    'feature_alpha': 0.5,
    'delta_weight': 0.4,
    'min_face_px': 40,
}
