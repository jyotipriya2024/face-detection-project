"""
Test and Examples Script for Face Detection System
"""

import cv2
import numpy as np
from pathlib import Path
import logging

from main import FaceDetectionSystem
from utils import load_image, save_image, get_image_files


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_basic_webcam():
    """
    Example 1: Basic real-time webcam detection
    """
    logger.info("=== Example 1: Basic Webcam Detection ===")
    
    system = FaceDetectionSystem()
    system.run_webcam(camera_id=0, display=True)


def example_2_image_processing():
    """
    Example 2: Process single image
    """
    logger.info("=== Example 2: Image Processing ===")
    
    # Create sample image directory
    sample_dir = Path("sample_images")
    if not sample_dir.exists():
        logger.warning("No sample_images directory found. Please add images.")
        return
    
    system = FaceDetectionSystem()
    
    image_files = get_image_files(str(sample_dir))
    for image_path in image_files[:5]:  # Process first 5 images
        logger.info(f"Processing: {image_path}")
        annotated = system.process_image(image_path, save_output=True)
        if annotated is not None:
            cv2.imshow("Detection Result", annotated)
            cv2.waitKey(2000)  # Show for 2 seconds
    
    cv2.destroyAllWindows()


def example_3_face_enrollment():
    """
    Example 3: Enroll person for recognition
    """
    logger.info("=== Example 3: Face Enrollment ===")
    
    system = FaceDetectionSystem()
    
    # Example person enrollment
    person_name = "John Doe"
    enrollment_images = [
        "path/to/john_1.jpg",
        "path/to/john_2.jpg",
        "path/to/john_3.jpg",
    ]
    
    # Check if images exist
    existing_images = [img for img in enrollment_images if Path(img).exists()]
    
    if existing_images:
        success = system.enroll_face(person_name, existing_images)
        if success:
            logger.info(f"Successfully enrolled {person_name}")
        else:
            logger.error(f"Failed to enroll {person_name}")
    else:
        logger.warning("No enrollment images found. Add images to enroll.")


def example_4_detection_analysis():
    """
    Example 4: Detailed analysis of detection results
    """
    logger.info("=== Example 4: Detailed Detection Analysis ===")
    
    system = FaceDetectionSystem()
    
    # Load a test image (or use default)
    test_image = load_image("test_image.jpg")
    if test_image is None:
        # Create a dummy image for demonstration
        logger.info("Creating dummy test image...")
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
    
    # Process frame
    results = system.process_frame(test_image)
    
    # Print analysis
    logger.info(f"Faces detected: {len(results['detections'])}")
    
    for idx, detection in enumerate(results['detections']):
        logger.info(f"\nFace #{idx + 1}:")
        logger.info(f"  Confidence: {detection['confidence']:.4f}")
        logger.info(f"  Bounding Box: {detection['bbox']}")
        
        if idx < len(results['landmarks']):
            landmarks = results['landmarks'][idx]
            logger.info(f"  Landmarks: {len(landmarks['landmarks'])} points")
        
        if idx < len(results['emotions']):
            emotion = results['emotions'][idx]
            emotion_str = ", ".join([f"{e}: {p:.2f}" for e, p in emotion.items()])
            logger.info(f"  Emotions: {emotion_str}")
        
        if idx < len(results['recognitions']):
            rec = results['recognitions'][idx]
            logger.info(f"  Recognition: {rec['name']} ({rec['confidence']:.2f})")


def example_5_batch_processing():
    """
    Example 5: Batch process image directory
    """
    logger.info("=== Example 5: Batch Processing ===")
    
    input_dir = "batch_input"
    output_dir = "batch_output"
    
    # Check if input directory exists
    if not Path(input_dir).exists():
        logger.warning(f"Input directory '{input_dir}' not found. Please create it.")
        return
    
    system = FaceDetectionSystem()
    
    image_files = get_image_files(input_dir)
    logger.info(f"Found {len(image_files)} images to process")
    
    Path(output_dir).mkdir(exist_ok=True)
    
    for idx, image_path in enumerate(image_files):
        try:
            logger.info(f"Processing [{idx+1}/{len(image_files)}]: {Path(image_path).name}")
            
            # Load image
            frame = cv2.imread(image_path)
            if frame is None:
                logger.warning(f"Could not load: {image_path}")
                continue
            
            # Process
            results = system.process_frame(frame)
            annotated = system.visualize_results(frame, results)
            
            # Save
            output_path = Path(output_dir) / f"detected_{Path(image_path).name}"
            cv2.imwrite(str(output_path), annotated)
            
            logger.info(f"  Detected {len(results['detections'])} faces")
        
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")


def example_6_video_processing():
    """
    Example 6: Process video file
    """
    logger.info("=== Example 6: Video Processing ===")
    
    video_path = "test_video.mp4"
    
    if not Path(video_path).exists():
        logger.warning(f"Video file '{video_path}' not found.")
        return
    
    system = FaceDetectionSystem()
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Could not open video: {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    logger.info(f"Video: {total_frames} frames @ {fps} FPS")
    
    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_num += 1
        if frame_num % 30 == 0:  # Process every 30th frame
            results = system.process_frame(frame)
            logger.info(f"Frame {frame_num}: {len(results['detections'])} faces detected")
        
        if frame_num >= 300:  # Process first 300 frames for demo
            break
    
    cap.release()
    logger.info(f"Processed {frame_num} frames")


def example_7_face_tracking():
    """
    Example 7: Face tracking and motion analysis
    """
    logger.info("=== Example 7: Face Tracking ===")
    
    system = FaceDetectionSystem()
    
    if not Path(0).exists():
        logger.warning("Camera not available")
        return
    
    cap = cv2.VideoCapture(0)
    frame_num = 0
    
    while frame_num < 100:  # Track for 100 frames
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_num += 1
        
        # Process frame
        results = system.process_frame(frame)
        
        # Analyze tracking
        if results['tracking']:
            logger.info(f"Frame {frame_num}: {len(results['tracking'])} faces being tracked")
            for face_id, (x, y) in results['tracking'].items():
                motion = system.face_tracker.get_motion_vector(face_id)
                if motion:
                    logger.info(f"  Face ID {face_id}: pos=({x:.1f}, {y:.1f}), motion={motion}")
        
        # Visualize
        annotated = system.visualize_results(frame, results)
        cv2.imshow("Face Tracking", annotated)
        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def example_8_performance_benchmark():
    """
    Example 8: Performance benchmarking
    """
    logger.info("=== Example 8: Performance Benchmark ===")
    
    import time
    
    system = FaceDetectionSystem()
    
    # Create dummy image
    frame = np.ones((720, 1280, 3), dtype=np.uint8) * 128
    
    num_iterations = 100
    
    logger.info(f"Running benchmark with {num_iterations} iterations...")
    
    start_time = time.time()
    
    for i in range(num_iterations):
        results = system.process_frame(frame)
    
    elapsed = time.time() - start_time
    avg_time = elapsed / num_iterations * 1000  # Convert to ms
    fps = num_iterations / elapsed
    
    logger.info(f"Average time per frame: {avg_time:.2f} ms")
    logger.info(f"Average FPS: {fps:.2f}")
    logger.info(f"Total time: {elapsed:.2f} seconds")


def main():
    """
    Run examples based on user selection
    """
    logger.info("Face Detection System - Examples")
    logger.info("=" * 50)
    
    examples = {
        '1': ('Webcam Detection', example_1_basic_webcam),
        '2': ('Image Processing', example_2_image_processing),
        '3': ('Face Enrollment', example_3_face_enrollment),
        '4': ('Detection Analysis', example_4_detection_analysis),
        '5': ('Batch Processing', example_5_batch_processing),
        '6': ('Video Processing', example_6_video_processing),
        '7': ('Face Tracking', example_7_face_tracking),
        '8': ('Performance Benchmark', example_8_performance_benchmark),
    }
    
    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Run All Examples")
    print("  q. Quit")
    
    choice = input("\nSelect example (0-8, q): ").strip().lower()
    
    if choice == 'q':
        logger.info("Exiting...")
        return
    
    if choice == '0':
        for name, func in examples.values():
            try:
                func()
            except Exception as e:
                logger.error(f"Error in {name}: {e}")
    elif choice in examples:
        try:
            name, func = examples[choice]
            func()
        except Exception as e:
            logger.error(f"Error: {e}")
    else:
        logger.error("Invalid selection")


if __name__ == "__main__":
    main()
