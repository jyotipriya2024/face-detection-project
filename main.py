"""
Optimized Machine Learning Model for Accurate Face Detection in Real-Time Application
Integrates optimized ML algorithms for robust real-time face detection, recognition, and analysis.
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from pathlib import Path

from face_detector import FaceDetector
from facial_landmarks import FacialLandmarksDetector
from face_recognizer import FaceRecognizer
from face_tracker import FaceTracker
from config import (
    FACE_DETECTION_CONFIG, LANDMARKS_CONFIG,
    RECOGNITION_CONFIG, TRACKING_CONFIG, VIDEO_CONFIG,
    DISPLAY_CONFIG, OUTPUT_CONFIG, LOGGING_CONFIG, ADVANCED_CONFIG
)


class FaceDetectionSystem:
    """
    Comprehensive face detection and recognition system.
    Combines detection, landmarks, recognition, and tracking.
    """
    
    def __init__(self, enable_tracking: bool = True, enable_recognition: bool = True,
                 enable_landmarks: bool = True):
        """
        Initialize face detection system.
        
        Args:
            enable_tracking: Enable face tracking
            enable_recognition: Enable face recognition
            enable_landmarks: Enable facial landmarks
        """
        # Initialize logger
        self._init_logger()
        self.logger.info("Initializing Face Detection System")
        
        # Initialize components
        self.face_detector = FaceDetector(FACE_DETECTION_CONFIG['confidence_threshold'])
        self.landmarks_detector = FacialLandmarksDetector() if enable_landmarks else None
        self.face_recognizer = FaceRecognizer() if enable_recognition else None
        self.face_tracker = FaceTracker() if enable_tracking else None
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'faces_detected': 0,
            'faces_recognized': 0,
            'fps': 0,
            'timestamp': datetime.now()
        }
        
        self.logger.info("System initialized successfully")
    
    def _init_logger(self):
        """Initialize logging."""
        logging.basicConfig(
            level=LOGGING_CONFIG['log_level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame with all detection and analysis.
        
        Args:
            frame: Input video frame
            
        Returns:
            Dictionary with all detection results
        """
        self.stats['frames_processed'] += 1
        
        results = {
            'frame': frame,
            'detections': [],
            'landmarks': [],
            'recognitions': [],
            'tracking': {}
        }
        
        # Detect faces
        detections = self.face_detector.detect_faces(frame)
        results['detections'] = detections
        self.stats['faces_detected'] += len(detections)
        
        # Extract face regions and process
        centroids = []
        for idx, detection in enumerate(detections):
            x_min, y_min, x_max, y_max = detection['bbox']
            face_image = frame[y_min:y_max, x_min:x_max]
            
            # Extract landmarks
            if self.landmarks_detector:
                landmarks = self.landmarks_detector.detect_landmarks(frame[max(0, y_min-20):min(frame.shape[0], y_max+20), 
                                                                               max(0, x_min-20):min(frame.shape[1], x_max+20)])
                if landmarks:
                    results['landmarks'].append(landmarks[0])
                    # Get centroid from landmarks for tracking
                    center = self.landmarks_detector.get_face_center(landmarks[0]['landmarks'])
                    centroids.append(center)
                else:
                    # Fallback to bbox center
                    centroids.append(((x_min + x_max) // 2, (y_min + y_max) // 2))
            
            # Recognize face
            if self.face_recognizer and face_image.size > 0:
                person_name, confidence = self.face_recognizer.recognize_face(face_image)
                results['recognitions'].append({
                    'name': person_name,
                    'confidence': confidence
                })
                if person_name:
                    self.stats['faces_recognized'] += 1
        
        # Update tracking
        if self.face_tracker and centroids:
            self.face_tracker.update(centroids)
            results['tracking'] = self.face_tracker.objects
        
        return results
    
    def visualize_results(self, frame: np.ndarray, results: Dict) -> np.ndarray:
        """
        Visualize detection results on frame with proper spacing.
        
        Args:
            frame: Original frame
            results: Detection results from process_frame
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        h, w = frame.shape[:2]
        
        # Draw detections (face boxes)
        if DISPLAY_CONFIG['show_face_detection']:
            annotated = self.face_detector.draw_detections(annotated, results['detections'])
        
        # Draw landmarks separately (not overlapping)
        if DISPLAY_CONFIG['show_landmarks'] and results['landmarks']:
            annotated = self.landmarks_detector.draw_landmarks(annotated, results['landmarks'],
                                                               DISPLAY_CONFIG['draw_contour'])
        
        # Draw identity information if available
        if DISPLAY_CONFIG['show_recognition'] and results['recognitions']:
            for detection, recognition in zip(results['detections'], results['recognitions']):
                x_min, y_min, x_max, y_max = detection['bbox']
                person_name = recognition['name'] if recognition['name'] else "Unknown"
                confidence = recognition['confidence']
                
                # Display identity label
                label = f"{person_name} ({confidence:.0%})"
                color = (0, 255, 0) if person_name != "Unknown" else (0, 0, 255)
                
                cv2.putText(annotated, label, (x_min, y_min - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Draw tracking (tracking is handled internally but not displayed as IDs)
        
        return annotated
    
    def run_webcam(self, camera_id: int = 0, display: bool = True):
        """
        Run face detection on webcam stream.
        
        Args:
            camera_id: ID of camera to use
            display: Whether to display results
        """
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            self.logger.error("Could not open camera")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_CONFIG['frame_width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_CONFIG['frame_height'])
        cap.set(cv2.CAP_PROP_FPS, VIDEO_CONFIG['fps'])
        
        self.logger.info(f"Starting webcam stream from camera {camera_id}")
        
        frame_count = 0
        import time
        prev_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                results = self.process_frame(frame)
                
                # Calculate FPS
                frame_count += 1
                curr_time = time.time()
                if curr_time - prev_time >= 1.0:
                    self.stats['fps'] = frame_count / (curr_time - prev_time)
                    frame_count = 0
                    prev_time = curr_time
                
                # Visualize
                if display:
                    annotated = self.visualize_results(frame, results)
                    cv2.imshow("Face Detection System", annotated)
                
                # Check for exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.logger.info("Exiting...")
                    break
        
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.logger.info(f"Processed {self.stats['frames_processed']} frames")
    
    def process_image(self, image_path: str, save_output: bool = True) -> np.ndarray:
        """
        Process a single image.
        
        Args:
            image_path: Path to image file
            save_output: Whether to save annotated image
            
        Returns:
            Annotated image
        """
        # Read image
        frame = cv2.imread(image_path)
        if frame is None:
            self.logger.error(f"Could not read image: {image_path}")
            return None
        
        # Process
        results = self.process_frame(frame)
        annotated = self.visualize_results(frame, results)
        
        # Save output
        if save_output:
            output_path = Path("output") / f"detected_{Path(image_path).name}"
            cv2.imwrite(str(output_path), annotated)
            self.logger.info(f"Saved annotated image to {output_path}")
        
        return annotated
    
    def enroll_face(self, person_name: str, image_paths: List[str]) -> bool:
        """
        Enroll a person for face recognition.
        
        Args:
            person_name: Name of person
            image_paths: List of face image paths
            
        Returns:
            Success status
        """
        if not self.face_recognizer:
            self.logger.warning("Face recognition not enabled")
            return False
        
        face_images = []
        for image_path in image_paths:
            frame = cv2.imread(image_path)
            if frame is None:
                self.logger.warning(f"Could not read image: {image_path}")
                continue
            
            # Detect and extract face
            detections = self.face_detector.detect_faces(frame)
            if detections:
                x_min, y_min, x_max, y_max = detections[0]['bbox']
                face = frame[y_min:y_max, x_min:x_max]
                face_images.append(face)
        
        if face_images:
            return self.face_recognizer.enroll_face(person_name, face_images)
        else:
            self.logger.error(f"No faces found to enroll for {person_name}")
            return False


def main():
    """Main entry point."""
    # Initialize system
    system = FaceDetectionSystem(
        enable_tracking=True,
        enable_recognition=True,
        enable_landmarks=True
    )
    
    # Run webcam
    system.run_webcam(camera_id=0, display=True)


if __name__ == "__main__":
    main()
