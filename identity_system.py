"""
Identity Detection System
Enroll faces, detect identities in real-time
"""

import cv2
import numpy as np
from pathlib import Path
from face_detector import FaceDetector
from face_recognizer import FaceRecognizer
from main import FaceDetectionSystem


class IdentityDetectionSystem:
    """
    Complete identity detection system for face recognition.
    """
    
    def __init__(self):
        """Initialize identity detection system."""
        self.system = FaceDetectionSystem(
            enable_tracking=True,
            enable_recognition=True,
            enable_landmarks=False
        )
        self.recognizer = FaceRecognizer()
        self.detector = FaceDetector()
        
    def enroll_identity_from_webcam(self, person_name: str, num_samples: int = 5):
        """
        Enroll a person's identity by capturing faces from webcam.
        
        Args:
            person_name: Name of the person to enroll
            num_samples: Number of samples to capture
        """
        print(f"\n{'='*60}")
        print(f"Enrolling Identity: {person_name}")
        print(f"{'='*60}")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open webcam")
            return False
        
        collected_faces = []
        frame_count = 0
        
        print(f"\n▶ Capturing {num_samples} face samples...")
        print("   Position your face in the center of the frame")
        print("   Press 'SPACE' to capture, 'ESC' to cancel")
        
        while len(collected_faces) < num_samples:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect faces in frame
            detections = self.detector.detect_faces(frame)
            result = self.detector.draw_detections(frame, detections)
            
            # Display countdown
            text = f"Collected: {len(collected_faces)}/{num_samples}"
            cv2.putText(result, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 
                       1.0, (0, 255, 0), 2)
            
            cv2.imshow(f"Enroll - {person_name}", result)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' ') and len(detections) > 0:
                # Get the largest face
                largest_face = max(detections, 
                                  key=lambda d: (d['bbox'][2]-d['bbox'][0]) * (d['bbox'][3]-d['bbox'][1]))
                x_min, y_min, x_max, y_max = largest_face['bbox']
                face_crop = frame[y_min:y_max, x_min:x_max]
                
                if face_crop.size > 0:
                    collected_faces.append(face_crop)
                    print(f"  ✓ Captured sample {len(collected_faces)}/{num_samples}")
            elif key == 27:  # ESC
                print("  Enrollment cancelled")
                cap.release()
                cv2.destroyAllWindows()
                return False
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
        if len(collected_faces) == num_samples:
            success = self.recognizer.enroll_face(person_name, collected_faces)
            if success:
                print(f"\n✓ Successfully enrolled {person_name}")
                return True
        
        print(f"\n❌ Failed to enroll {person_name}")
        return False
    
    def run_identity_detection(self, camera_id: int = 0, display: bool = True):
        """
        Run identity detection on webcam stream.
        
        Args:
            camera_id: Camera ID to use
            display: Whether to display results
        """
        print(f"\n{'='*60}")
        print("Identity Detection - Press 'Q' to quit")
        print(f"{'='*60}\n")
        
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print("❌ Cannot open webcam")
            return
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect faces
            detections = self.detector.detect_faces(frame)
            result = self.detector.draw_detections(frame, detections)
            
            # Recognize identities
            identities = []
            for detection in detections:
                x_min, y_min, x_max, y_max = detection['bbox']
                face_crop = frame[y_min:y_max, x_min:x_max]
                
                if face_crop.size > 0:
                    person_name, confidence = self.recognizer.recognize_face(face_crop)
                    identities.append((person_name, confidence))
            
            # Draw identity information
            for detection, identity in zip(detections, identities):
                x_min, y_min, x_max, y_max = detection['bbox']
                person_name, confidence = identity
                
                if person_name:
                    # Draw identity label
                    label = f"{person_name} ({confidence:.0%})"
                    color = (0, 255, 0)
                    
                    cv2.putText(result, label, (x_min, y_min - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            # Display statistics
            recognized_count = sum(1 for _, name, _ in [(d, i[0], i[1]) for d, i in zip(detections, identities)] if name)
            stats_text = f"Faces: {len(detections)} | Recognized: {recognized_count}"
            cv2.putText(result, stats_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                       1.0, (0, 255, 0), 2)
            
            if display:
                cv2.imshow("Identity Detection", result)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"\nProcessed {frame_count} frames")
        print("Identity detection stopped")


def main():
    """
    Main function for identity detection.
    """
    print("=" * 60)
    print("Face Identity Detection System")
    print("=" * 60)
    
    system = IdentityDetectionSystem()
    
    print("\n1. Enroll New Identity")
    print("2. Run Identity Detection")
    print("3. List Enrolled Identities")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            person_name = input("Enter person's name: ").strip()
            if person_name:
                system.enroll_identity_from_webcam(person_name, num_samples=5)
        
        elif choice == '2':
            system.run_identity_detection()
        
        elif choice == '3':
            enrolled = system.recognizer.enrolled_faces
            if enrolled:
                print(f"\nEnrolled Identities ({len(enrolled)}):")
                for name, embeddings in enrolled.items():
                    print(f"  • {name}: {len(embeddings)} samples")
            else:
                print("\nNo identities enrolled yet")
        
        elif choice == '4':
            print("\nExiting...")
            break
        
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
