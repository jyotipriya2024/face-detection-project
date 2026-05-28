"""
Face Detection and Recognition System
Robust ML-based face detection with recognition, landmarks, tracking, and emotion detection.
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import mediapipe as mp
import os
import json
from datetime import datetime


class FaceDetector:
    """
    Robust face detection using MediaPipe and OpenCV.
    Handles multiple faces with high accuracy.
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize face detector.
        
        Args:
            confidence_threshold: Minimum confidence for face detection (0-1)
        """
        self.confidence_threshold = confidence_threshold
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        )
        # Initialize MediaPipe face detection with fallback
        self.face_detector = None
        self.mp_drawing = None
        try:
            # Try to use MediaPipe solutions
            mp_face_det = getattr(mp, 'solutions', None)
            if mp_face_det:
                self.mp_face_detection = mp.solutions.face_detection
                self.face_detector = self.mp_face_detection.FaceDetection(
                    model_selection=1,
                    min_detection_confidence=confidence_threshold
                )
                self.mp_drawing = mp.solutions.drawing_utils
        except Exception as e:
            print(f"MediaPipe solutions not available, using OpenCV: {e}")
    
    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all faces in image.
        
        Args:
            image: Input image (BGR format from OpenCV)
            
        Returns:
            List of detected faces with bounding boxes and confidence
        """
        # Use cascade if MediaPipe not available
        if self.face_detector is None:
            return self._detect_faces_cascade(image)
        
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_detector.process(rgb_image)
            
            detections = []
            if results.detections:
                h, w, _ = image.shape
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    
                    # Convert to pixel coordinates
                    x_min = int(bbox.xmin * w)
                    y_min = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)
                    
                    # Ensure coordinates are within bounds
                    x_min = max(0, x_min)
                    y_min = max(0, y_min)
                    x_max = min(w, x_min + width)
                    y_max = min(h, y_min + height)
                    
                    detections.append({
                        'bbox': (x_min, y_min, x_max, y_max),
                        'confidence': detection.score[0] if detection.score else 0.0,
                        'landmarks': detection.location_data.relative_keypoints
                    })
            
            return detections
        except Exception:
            return self._detect_faces_cascade(image)
    
    def _detect_faces_cascade(self, image: np.ndarray) -> List[Dict]:
        """Fallback face detection using OpenCV Haar Cascades."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast for better detection
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Try multiple scale factors for better detection
        detections = []
        h, w, _ = image.shape
        
        # First pass: aggressive detection
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20), maxSize=(w-10, h-10)
        )
        
        for (x, y, fw, fh) in faces:
            detections.append({
                'bbox': (x, y, x + fw, y + fh),
                'confidence': 0.85,
                'landmarks': None
            })
        
        # Second pass: if no faces found, try more relaxed parameters
        if len(detections) == 0:
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.08, minNeighbors=2, minSize=(15, 15), maxSize=(w-5, h-5)
            )
            
            for (x, y, fw, fh) in faces:
                detections.append({
                    'bbox': (x, y, x + fw, y + fh),
                    'confidence': 0.75,
                    'landmarks': None
                })
        
        # Remove duplicate/overlapping detections
        detections = self._remove_overlapping_detections(detections)
        
        return detections
    
    def _remove_overlapping_detections(self, detections: List[Dict]) -> List[Dict]:
        """Remove overlapping face detections, keeping the larger ones."""
        if len(detections) <= 1:
            return detections
        
        filtered = []
        used = set()
        
        # Sort by area (larger first)
        sorted_dets = sorted(detections, 
                            key=lambda d: (d['bbox'][2]-d['bbox'][0]) * (d['bbox'][3]-d['bbox'][1]), 
                            reverse=True)
        
        for i, det1 in enumerate(sorted_dets):
            if i in used:
                continue
            
            filtered.append(det1)
            
            # Mark overlapping detections as used
            x1_min, y1_min, x1_max, y1_max = det1['bbox']
            area1 = (x1_max - x1_min) * (y1_max - y1_min)
            
            for j, det2 in enumerate(sorted_dets[i+1:], start=i+1):
                if j in used:
                    continue
                    
                x2_min, y2_min, x2_max, y2_max = det2['bbox']
                
                # Calculate intersection
                inter_x_min = max(x1_min, x2_min)
                inter_y_min = max(y1_min, y2_min)
                inter_x_max = min(x1_max, x2_max)
                inter_y_max = min(y1_max, y2_max)
                
                if inter_x_max > inter_x_min and inter_y_max > inter_y_min:
                    intersection = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
                    # If >30% overlap, mark as duplicate
                    if intersection > 0.3 * area1:
                        used.add(j)
        
        return filtered
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes on image.
        
        Args:
            image: Input image
            detections: List of detected faces
            
        Returns:
            Image with drawn bounding boxes
        """
        result = image.copy()
        for detection in detections:
            x_min, y_min, x_max, y_max = detection['bbox']
            # Draw rectangle only
            cv2.rectangle(result, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        
        return result
