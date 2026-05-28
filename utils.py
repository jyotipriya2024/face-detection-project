"""
Utility functions for Face Detection System
"""

import cv2
import numpy as np
import os
from pathlib import Path
from typing import List, Tuple, Optional
import logging


logger = logging.getLogger(__name__)


def load_image(image_path: str) -> Optional[np.ndarray]:
    """
    Load image from file.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Image array or None if failed
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not load image: {image_path}")
            return None
        return image
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None


def save_image(image: np.ndarray, output_path: str) -> bool:
    """
    Save image to file.
    
    Args:
        image: Image array
        output_path: Output file path
        
    Returns:
        Success status
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, image)
        logger.info(f"Saved image to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving image to {output_path}: {e}")
        return False


def crop_face(image: np.ndarray, bbox: Tuple[int, int, int, int], 
              padding: float = 0.1) -> np.ndarray:
    """
    Crop face from image with optional padding.
    
    Args:
        image: Input image
        bbox: Bounding box (x_min, y_min, x_max, y_max)
        padding: Padding ratio relative to face size
        
    Returns:
        Cropped face image
    """
    x_min, y_min, x_max, y_max = bbox
    width = x_max - x_min
    height = y_max - y_min
    
    pad_x = int(width * padding)
    pad_y = int(height * padding)
    
    x_min = max(0, x_min - pad_x)
    y_min = max(0, y_min - pad_y)
    x_max = min(image.shape[1], x_max + pad_x)
    y_max = min(image.shape[0], y_max + pad_y)
    
    return image[y_min:y_max, x_min:x_max]


def resize_image(image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    """
    Resize image to specified size.
    
    Args:
        image: Input image
        size: Target size (width, height)
        
    Returns:
        Resized image
    """
    return cv2.resize(image, size, interpolation=cv2.INTER_LINEAR)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize image to [0, 1] range.
    
    Args:
        image: Input image
        
    Returns:
        Normalized image
    """
    return image.astype(np.float32) / 255.0


def denormalize_image(image: np.ndarray) -> np.ndarray:
    """
    Denormalize image from [0, 1] range to [0, 255].
    
    Args:
        image: Normalized image
        
    Returns:
        Denormalized image
    """
    return (np.clip(image, 0, 1) * 255).astype(np.uint8)


def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    Apply histogram equalization for better contrast.
    
    Args:
        image: Input image
        
    Returns:
        Processed image
    """
    if len(image.shape) == 3:
        # Color image - convert to HSV and equalize V channel
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.equalizeHist(v)
        hsv = cv2.merge([h, s, v])
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    else:
        # Grayscale image
        return cv2.equalizeHist(image)


def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply Gaussian blur for smoothing.
    
    Args:
        image: Input image
        kernel_size: Kernel size (must be odd)
        
    Returns:
        Blurred image
    """
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def get_image_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Get all image files in directory.
    
    Args:
        directory: Directory path
        extensions: List of file extensions to include
        
    Returns:
        List of image file paths
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    image_files = []
    path = Path(directory)
    
    for ext in extensions:
        image_files.extend(path.glob(f'*{ext}'))
        image_files.extend(path.glob(f'*{ext.upper()}'))
    
    return [str(f) for f in sorted(set(image_files))]


def get_video_info(video_path: str) -> dict:
    """
    Get information about video file.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video info
    """
    cap = cv2.VideoCapture(video_path)
    
    info = {
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
    }
    
    cap.release()
    return info


def draw_bbox(image: np.ndarray, bbox: Tuple[int, int, int, int], 
              label: str = "", color: Tuple[int, int, int] = (0, 255, 0),
              thickness: int = 2) -> np.ndarray:
    """
    Draw bounding box on image.
    
    Args:
        image: Input image
        bbox: Bounding box coordinates
        label: Label text
        color: Box color (BGR)
        thickness: Line thickness
        
    Returns:
        Image with drawn bbox
    """
    result = image.copy()
    x_min, y_min, x_max, y_max = bbox
    
    cv2.rectangle(result, (x_min, y_min), (x_max, y_max), color, thickness)
    
    if label:
        cv2.putText(result, label, (x_min, y_min - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    
    return result


def draw_circle(image: np.ndarray, center: Tuple[int, int], radius: int = 5,
               color: Tuple[int, int, int] = (0, 255, 0), thickness: int = -1) -> np.ndarray:
    """
    Draw circle on image.
    
    Args:
        image: Input image
        center: Circle center (x, y)
        radius: Circle radius
        color: Circle color (BGR)
        thickness: -1 for filled circle
        
    Returns:
        Image with drawn circle
    """
    result = image.copy()
    cv2.circle(result, tuple(map(int, center)), radius, color, thickness)
    return result


def batch_process_images(input_dir: str, output_dir: str, process_func, 
                        extensions: List[str] = None) -> int:
    """
    Process all images in a directory.
    
    Args:
        input_dir: Input directory
        output_dir: Output directory
        process_func: Function to apply to each image
        extensions: Image extensions to process
        
    Returns:
        Number of processed images
    """
    image_files = get_image_files(input_dir, extensions)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    count = 0
    for image_path in image_files:
        try:
            image = load_image(image_path)
            if image is not None:
                processed = process_func(image)
                output_path = Path(output_dir) / Path(image_path).name
                save_image(processed, str(output_path))
                count += 1
                logger.info(f"Processed {count}/{len(image_files)}: {image_path}")
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
    
    return count


def calculate_iou(bbox1: Tuple[int, int, int, int], 
                 bbox2: Tuple[int, int, int, int]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bboxes.
    
    Args:
        bbox1: First bbox (x_min, y_min, x_max, y_max)
        bbox2: Second bbox (x_min, y_min, x_max, y_max)
        
    Returns:
        IoU value (0-1)
    """
    x_min1, y_min1, x_max1, y_max1 = bbox1
    x_min2, y_min2, x_max2, y_max2 = bbox2
    
    # Calculate intersection
    inter_x_min = max(x_min1, x_min2)
    inter_y_min = max(y_min1, y_min2)
    inter_x_max = min(x_max1, x_max2)
    inter_y_max = min(y_max1, y_max2)
    
    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return 0.0
    
    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    
    # Calculate union
    area1 = (x_max1 - x_min1) * (y_max1 - y_min1)
    area2 = (x_max2 - x_min2) * (y_max2 - y_min2)
    union_area = area1 + area2 - inter_area
    
    if union_area == 0:
        return 0.0
    
    return inter_area / union_area
