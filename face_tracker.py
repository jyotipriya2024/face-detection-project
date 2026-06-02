"""
Face Tracking Module
Tracks faces across frames using centroid tracking and appearance matching.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import deque
from scipy.spatial import distance


class FaceTracker:
    """
    Tracks faces across video frames using centroid tracking.
    Maintains consistent face IDs across frames.
    """
    
    def __init__(self, max_disappeared: int = 50, max_distance: float = 100):
        """
        Initialize face tracker.
        
        Args:
            max_disappeared: Maximum frames a face can disappear before removing
            max_distance: Maximum distance for centroid matching
        """
        self.next_object_id = 0
        self.objects = {}  # {id: centroid}
        self.disappeared = {}  # {id: frame_count}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.history = {}  # {id: deque of centroids}
        self.history_length = 30
    
    def register(self, centroid: Tuple[int, int]):
        """
        Register a new face.
        
        Args:
            centroid: (x, y) coordinates of face center
        """
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.history[self.next_object_id] = deque(maxlen=self.history_length)
        self.history[self.next_object_id].append(centroid)
        self.next_object_id += 1
    
    def deregister(self, object_id: int):
        """
        Deregister a face.
        
        Args:
            object_id: ID of face to remove
        """
        del self.objects[object_id]
        del self.disappeared[object_id]
        del self.history[object_id]
    
    def update(self, centroids: List[Tuple[int, int]]) -> Dict[int, Tuple[int, int]]:
        """
        Update tracker with new centroids.
        
        Args:
            centroids: List of (x, y) centroids detected in current frame
            
        Returns:
            Dictionary mapping face IDs to centroids
        """
        if len(centroids) == 0:
            # Mark all as disappeared
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects
        
        # Match centroids to existing objects
        if len(self.objects) == 0:
            for i in range(0, len(centroids)):
                self.register(centroids[i])
        else:
            # Get IDs and centroids
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Compute distance between existing and new centroids
            d = distance.cdist(np.array(object_centroids), np.array(centroids))
            
            # Sort by distance and match
            rows = d.min(axis=1).argsort()
            cols = d.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if d[row, col] > self.max_distance:
                    continue
                
                object_id = object_ids[row]
                self.objects[object_id] = centroids[col]
                self.disappeared[object_id] = 0
                self.history[object_id].append(centroids[col])
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Register new centroids
            unused_cols = set(range(0, len(centroids))).difference(used_cols)
            for col in unused_cols:
                self.register(centroids[col])
            
            # Deregister disappeared objects
            unused_rows = set(range(0, len(object_centroids))).difference(used_rows)
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
        
        return self.objects
    
    def get_motion_vector(self, object_id: int) -> Optional[Tuple[int, int]]:
        """
        Get motion vector (velocity) for a face.
        
        Args:
            object_id: Face ID
            
        Returns:
            Tuple of (vx, vy) or None if not enough history
        """
        if object_id not in self.history or len(self.history[object_id]) < 2:
            return None
        
        history = list(self.history[object_id])
        curr = history[-1]
        prev = history[-2]
        
        vx = curr[0] - prev[0]
        vy = curr[1] - prev[1]
        
        return (vx, vy)
    
    def predict_position(self, object_id: int, frames_ahead: int = 1) -> Optional[Tuple[int, int]]:
        """
        Predict future position of a face using linear motion model.
        
        Args:
            object_id: Face ID
            frames_ahead: Number of frames to predict ahead
            
        Returns:
            Predicted (x, y) position or None
        """
        motion = self.get_motion_vector(object_id)
        if motion is None or object_id not in self.objects:
            return None
        
        x, y = self.objects[object_id]
        vx, vy = motion
        
        pred_x = x + vx * frames_ahead
        pred_y = y + vy * frames_ahead
        
        return (int(pred_x), int(pred_y))


class KalmanFilterTracker:
    """
    Alternative tracker using Kalman filter for smoother tracking.
    Better for handling occlusions and sudden movements.
    """
    
    def __init__(self):
        """Initialize Kalman filter tracker."""
        self.trackers = {}  # {id: KalmanFilter}
        self.next_id = 0
        self.frame_count = 0
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of detection dicts with 'bbox' key
            
        Returns:
            List of tracked faces with IDs
        """
        self.frame_count += 1
        tracked_faces = []
        
        # TODO: Implement Kalman filter based tracking
        # This is a placeholder for more advanced tracking
        
        return tracked_faces
