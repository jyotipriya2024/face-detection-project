"""
Identity Detection System Test
Demonstrates face enrollment and recognition
"""

import cv2
import numpy as np
from pathlib import Path
from identity_system import IdentityDetectionSystem


def test_identity_detection():
    """
    Test the identity detection system with demo mode.
    """
    print("=" * 70)
    print("Identity Detection System - Test Mode")
    print("=" * 70)
    
    system = IdentityDetectionSystem()
    
    # Check enrolled faces
    enrolled_count = len(system.recognizer.enrolled_faces)
    
    print(f"\n▶ System Status:")
    print(f"   - Enrolled identities: {enrolled_count}")
    print(f"   - Face database: {system.recognizer.face_database_path}")
    
    if enrolled_count > 0:
        print(f"\n▶ Enrolled People:")
        for name, embeddings in system.recognizer.enrolled_faces.items():
            print(f"   • {name}: {len(embeddings)} samples")
    
    print("\n" + "=" * 70)
    print("Test Options:")
    print("=" * 70)
    print("\n1. Enroll a new identity (capture from webcam)")
    print("2. Run identity detection on webcam")
    print("3. Test with synthetic faces")
    print("4. View enrolled identities")
    print("5. Exit")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            person_name = input("\nEnter name to enroll: ").strip()
            if person_name:
                print("\n▶ Enrollment Process:")
                print("   Press SPACE to capture face")
                print("   Press ESC to cancel")
                system.enroll_identity_from_webcam(person_name, num_samples=3)
        
        elif choice == '2':
            print("\n▶ Starting Identity Detection")
            print("   Press 'Q' to stop")
            system.run_identity_detection(camera_id=0, display=True)
        
        elif choice == '3':
            test_synthetic_faces(system)
        
        elif choice == '4':
            enrolled = system.recognizer.enrolled_faces
            if enrolled:
                print(f"\n✓ Enrolled Identities: {len(enrolled)}")
                for name, embeddings in enrolled.items():
                    print(f"  • {name}: {len(embeddings)} face samples")
            else:
                print("\n⚠ No identities enrolled yet")
        
        elif choice == '5':
            print("\nExiting...")
            break
        
        else:
            print("Invalid option, try again")


def test_synthetic_faces(system):
    """
    Test identity detection with synthetic face images.
    """
    print("\n" + "=" * 70)
    print("Synthetic Face Test")
    print("=" * 70)
    
    # Create a synthetic test face
    print("\n▶ Creating synthetic test face...")
    
    test_face = np.ones((256, 256, 3), dtype=np.uint8) * 220
    
    # Add simple face features
    center_x, center_y = 128, 128
    radius = 80
    
    # Face oval
    cv2.ellipse(test_face, (center_x, center_y), (radius, radius + 20), 
                0, 0, 360, (150, 100, 80), -1)
    
    # Eyes
    cv2.circle(test_face, (center_x - 30, center_y - 20), 15, (100, 100, 100), -1)
    cv2.circle(test_face, (center_x + 30, center_y - 20), 15, (100, 100, 100), -1)
    cv2.circle(test_face, (center_x - 30, center_y - 20), 8, (0, 0, 0), -1)
    cv2.circle(test_face, (center_x + 30, center_y - 20), 8, (0, 0, 0), -1)
    
    # Nose
    cv2.circle(test_face, (center_x, center_y + 10), 8, (130, 80, 60), -1)
    
    # Mouth (smile)
    cv2.ellipse(test_face, (center_x, center_y + 40), (25, 15), 0, 0, 180, (100, 50, 50), 2)
    
    cv2.imwrite("test_identity_face.jpg", test_face)
    print("  ✓ Created test_identity_face.jpg")
    
    # Test recognition
    print("\n▶ Testing face recognition on synthetic face...")
    
    person_name, confidence = system.recognizer.recognize_face(test_face)
    
    print(f"\n  Recognition Result:")
    if person_name:
        print(f"    • Identity: {person_name}")
        print(f"    • Confidence: {confidence:.0%}")
        print(f"    • Status: ✓ RECOGNIZED")
    else:
        print(f"    • Identity: Unknown")
        print(f"    • Status: ⚠ NOT RECOGNIZED")
        print(f"    • Reason: No matching enrolled identity")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        test_identity_detection()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
