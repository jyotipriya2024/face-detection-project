"""
Facial Landmarks Detection Module
Extracts facial landmarks (eyes, nose, mouth, jawline) for detailed face analysis.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import mediapipe as mp


class FacialLandmarksDetector:
    """
    Detects and manages facial landmarks using MediaPipe.
    Provides 468 facial landmarks with high precision.
    """
    
    def __init__(self):
        """Initialize facial landmarks detector."""
        self.face_mesh = None
        try:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=10,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except Exception as e:
            print(f"MediaPipe face mesh not available: {e}")
            self.mp_face_mesh = None
        
        # Define landmark groups
        self.landmark_groups = {
            'left_eye': list(range(362, 383, 1)),
            'right_eye': list(range(33, 54, 1)),
            'mouth': list(range(61, 186, 1)),
            'left_eyebrow': list(range(276, 283, 1)),
            'right_eyebrow': list(range(46, 53, 1)),
            'nose': list(range(1, 31, 1)),
            'face_contour': list(range(0, 17, 1))
        }
    
    def detect_landmarks(self, image: np.ndarray) -> List[Dict]:
        """
        Detect facial landmarks in image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of landmarks for each detected face
        """
        if self.face_mesh is None:
            return []  # Return empty if MediaPipe not available
        
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_image)
            
            landmarks_list = []
            if results.multi_face_landmarks:
                h, w, _ = image.shape
                for face_landmarks in results.multi_face_landmarks:
                    landmarks = []
                    for landmark in face_landmarks.landmark:
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        z = landmark.z
                        landmarks.append({'x': x, 'y': y, 'z': z})
                    
                    landmarks_list.append({
                        'landmarks': landmarks,
                        'landmark_groups': self._extract_landmark_groups(landmarks)
                    })
            
            return landmarks_list
        except Exception as e:
            print(f"Error detecting landmarks: {e}")
            return []
    
    def _extract_landmark_groups(self, landmarks: List[Dict]) -> Dict[str, List[Tuple]]:
        """Extract grouped landmarks for easier access."""
        groups = {}
        for group_name, indices in self.landmark_groups.items():
            group_points = []
            for idx in indices:
                if idx < len(landmarks):
                    l = landmarks[idx]
                    group_points.append((l['x'], l['y']))
            groups[group_name] = group_points
        return groups
    
    def draw_landmarks(self, image: np.ndarray, landmarks_data: List[Dict],
                      draw_contour: bool = True) -> np.ndarray:
        """
        Draw facial landmarks on image.
        
        Args:
            image: Input image
            landmarks_data: Detected landmarks
            draw_contour: Whether to draw face contour
            
        Returns:
            Image with drawn landmarks
        """
        result = image.copy()
        
        for face_landmarks in landmarks_data:
            landmarks = face_landmarks['landmarks']
            groups = face_landmarks['landmark_groups']
            
            # Draw eyes
            for eye_name in ['left_eye', 'right_eye']:
                points = np.array(groups[eye_name], dtype=np.int32)
                cv2.polylines(result, [points], True, (0, 255, 0), 1)
            
            # Draw eyebrows
            for brow_name in ['left_eyebrow', 'right_eyebrow']:
                points = np.array(groups[brow_name], dtype=np.int32)
                cv2.polylines(result, [points], False, (255, 0, 0), 1)
            
            # Draw mouth
            mouth_points = np.array(groups['mouth'], dtype=np.int32)
            cv2.polylines(result, [mouth_points], True, (255, 0, 255), 1)
            
            # Draw nose
            nose_points = np.array(groups['nose'], dtype=np.int32)
            cv2.polylines(result, [nose_points], False, (0, 255, 255), 1)
            
            # Draw face contour if requested
            if draw_contour:
                contour_points = np.array(groups['face_contour'], dtype=np.int32)
                cv2.polylines(result, [contour_points], False, (128, 128, 0), 2)
            
            # Draw all landmark points
            for landmark in landmarks:
                cv2.circle(result, (landmark['x'], landmark['y']), 1, (0, 0, 255), -1)
        
        return result
    
    def get_face_center(self, landmarks: List[Dict]) -> Tuple[int, int]:
        """Calculate center of face from landmarks."""
        all_x = [l['x'] for l in landmarks]
        all_y = [l['y'] for l in landmarks]
        center_x = int(np.mean(all_x))
        center_y = int(np.mean(all_y))
        return center_x, center_y
    
    def get_face_bounding_box(self, landmarks: List[Dict]) -> Tuple[int, int, int, int]:
        """Get bounding box from landmarks."""
        all_x = [l['x'] for l in landmarks]
        all_y = [l['y'] for l in landmarks]
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        return x_min, y_min, x_max, y_max
