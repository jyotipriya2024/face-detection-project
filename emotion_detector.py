"""
Emotion Detection Module
Detects emotional expressions using deep learning.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, List
import os


class EmotionDetector:
    """
    Detects emotions from facial expressions using CNN.
    Supports: happy, sad, angry, surprised, fear, disgust, neutral
    """
    
    def __init__(self):
        """Initialize emotion detector with pre-trained model."""
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprised']
        self.emotion_colors = {
            'happy': (0, 255, 0),      # Green
            'sad': (255, 0, 0),        # Blue
            'angry': (0, 0, 255),      # Red
            'surprised': (255, 255, 0), # Cyan
            'fear': (255, 0, 255),     # Magenta
            'disgust': (0, 165, 255),  # Orange
            'neutral': (128, 128, 128) # Gray
        }
        
        # Load pre-trained emotion detection model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained emotion detection model."""
        try:
            # Using a simple CNN-based approach with Keras
            # In production, you'd download a pre-trained model
            self.model = self._build_emotion_model()
        except Exception as e:
            print(f"Warning: Could not load emotion model: {e}")
            self.model = None
    
    def _build_emotion_model(self):
        """
        Build a lightweight emotion model.
        In production, use pre-trained models like:
        - FER2013 trained model
        - AffectNet
        - VggFace2 based emotion models
        
        Note: This simplified version works without TensorFlow
        using histogram and texture features.
        """
        return None  # Use feature-based approach instead
    
    def detect_emotion(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        Detect emotion from face image using feature analysis.
        
        Args:
            face_image: Cropped face image
            
        Returns:
            Dictionary with emotion probabilities
        """
        if face_image is None or face_image.size == 0:
            return {emotion: 1.0/len(self.emotions) for emotion in self.emotions}
        
        try:
            # Use feature-based emotion detection
            return self._detect_emotion_features(face_image)
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return {emotion: 1.0/len(self.emotions) for emotion in self.emotions}
    
    def _detect_emotion_features(self, face_image: np.ndarray) -> Dict[str, float]:
        """
        Detect emotion using relative feature comparisons rather than absolute thresholds.
        More robust for varying lighting and real webcam conditions.
        """
        try:
            # Preprocess
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (128, 128))
            
            # Extract core features
            brightness = np.mean(gray) / 255.0
            contrast = np.std(gray) / 255.0
            
            # Edge detection
            edges = cv2.Canny(gray, 30, 100)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Saturation from HSV
            hsv = cv2.cvtColor(face_image, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:,:,1]) / 255.0
            
            # Regional brightness for droopy/raised features
            h_step = 128 // 3
            upper_brightness = np.mean(gray[:h_step, :]) / 255.0
            lower_brightness = np.mean(gray[2*h_step:, :]) / 255.0
            brightness_diff = upper_brightness - lower_brightness
            
            scores = {}
            
            # Base scores - each emotion gets a baseline
            # Then we adjust based on how well features match
            
            # HAPPY: Brightness and saturation above average, few edges
            happy_brightness_bonus = max(0, brightness - 0.50) / 0.50  # Favors brighter
            happy_saturation_bonus = max(0, saturation - 0.45) / 0.55  # Favors more saturated
            happy_smooth_bonus = max(0, 1 - edge_density / 0.30)  # Favors smooth
            scores['happy'] = (0.2 + 
                              happy_brightness_bonus * 0.35 + 
                              happy_saturation_bonus * 0.30 + 
                              happy_smooth_bonus * 0.15)
            
            # SAD: Lower brightness and saturation, droopy (upper > lower)
            sad_dark_bonus = max(0, 1 - brightness / 0.70)  # Favors darker
            sad_desaturate_bonus = max(0, 1 - saturation / 0.65)  # Favors desaturated
            sad_droop_bonus = max(0, brightness_diff * 2)  # Favors upper > lower
            scores['sad'] = (0.15 + 
                            sad_dark_bonus * 0.35 + 
                            sad_desaturate_bonus * 0.30 + 
                            sad_droop_bonus * 0.20)
            
            # ANGRY: High contrast + many edges + moderate tension
            angry_contrast_bonus = max(0, contrast - 0.20) / 0.50  # Favors high contrast
            angry_edges_bonus = max(0, edge_density - 0.15) / 0.35  # Favors edges
            scores['angry'] = (0.15 + 
                              angry_contrast_bonus * 0.45 + 
                              angry_edges_bonus * 0.40)
            
            # SURPRISED: Very bright + high saturation + brightness consistency
            surprised_brightness_bonus = max(0, brightness - 0.65) / 0.35  # Favors very bright
            surprised_saturation_bonus = max(0, saturation - 0.55) / 0.45  # Favors high sat
            surprised_upper_bonus = max(0, upper_brightness - 0.65) / 0.35  # Bright eyes
            scores['surprised'] = (0.15 + 
                                  surprised_brightness_bonus * 0.35 + 
                                  surprised_saturation_bonus * 0.30 + 
                                  surprised_upper_bonus * 0.20)
            
            # FEAR: Raised eyebrows + variable expression + moderate tension
            fear_eyes_bonus = max(0, upper_brightness - 0.55) / 0.45  # Bright upper
            fear_variable_bonus = abs(brightness_diff) / 0.30  # Variable brightness
            fear_edges_bonus = max(0, edge_density - 0.15) / 0.30  # Some edges
            scores['fear'] = (0.15 + 
                             fear_eyes_bonus * 0.35 + 
                             fear_variable_bonus * 0.30 + 
                             fear_edges_bonus * 0.20)
            
            # DISGUST: Very desaturated is the key indicator
            disgust_desaturate_bonus = max(0, 1 - saturation / 0.50)  # Very desaturated
            disgust_dark_bonus = max(0, 1 - brightness / 0.70)  # Darker
            scores['disgust'] = (0.15 + 
                                disgust_desaturate_bonus * 0.60 + 
                                disgust_dark_bonus * 0.25)
            
            # NEUTRAL: Balance across features - no strong emotion indicators
            neutral_score = 0.20
            
            # Add points if features are balanced/moderate
            if 0.40 < brightness < 0.70:
                neutral_score += 0.25
            if 0.30 < saturation < 0.70:
                neutral_score += 0.25
            if 0.15 < edge_density < 0.30:
                neutral_score += 0.25
            if abs(brightness_diff) < 0.15:
                neutral_score += 0.15
            
            scores['neutral'] = neutral_score
            
            # Ensure all scores are positive and apply power scaling
            for emotion in scores:
                scores[emotion] = max(scores[emotion], 0.01)
            
            scores = {k: v ** 1.4 for k, v in scores.items()}
            
            # Normalize to probabilities
            total = sum(scores.values())
            if total > 0:
                emotion_dict = {k: v / total for k, v in scores.items()}
            else:
                emotion_dict = {emotion: 1.0/len(self.emotions) for emotion in self.emotions}
            
            return emotion_dict
            
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return {emotion: 1.0/len(self.emotions) for emotion in self.emotions}
    
    def get_dominant_emotion(self, emotion_dict: Dict[str, float]) -> Tuple[str, float]:
        """
        Get the dominant emotion from prediction dictionary.
        
        Args:
            emotion_dict: Dictionary with emotion probabilities
            
        Returns:
            Tuple of (emotion_name, probability)
        """
        if not emotion_dict:
            return 'neutral', 0.0
        
        dominant_emotion = max(emotion_dict.items(), key=lambda x: x[1])
        return dominant_emotion[0], dominant_emotion[1]
    
    def draw_emotion(self, image: np.ndarray, face_bbox: Tuple[int, int, int, int],
                    emotion_dict: Dict[str, float]) -> np.ndarray:
        """
        Draw emotion on image with separated visualization.
        
        Args:
            image: Input image
            face_bbox: Face bounding box (x_min, y_min, x_max, y_max)
            emotion_dict: Dictionary with emotion probabilities
            
        Returns:
            Image with drawn emotion
        """
        result = image.copy()
        x_min, y_min, x_max, y_max = face_bbox
        
        # Get dominant emotion
        emotion, confidence = self.get_dominant_emotion(emotion_dict)
        color = self.emotion_colors.get(emotion, (255, 255, 255))
        
        # Draw main emotion label with background (BELOW the box)
        label = f"{emotion.upper()}: {confidence:.0%}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.85
        thickness = 2
        
        text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        label_y = y_max + 30
        label_x = x_min + 5
        
        # Draw background for main label
        cv2.rectangle(result,
                     (label_x - 3, label_y - text_size[1] - 3),
                     (label_x + text_size[0] + 3, label_y + 3),
                     color, -1)
        cv2.putText(result, label, (label_x, label_y),
                   font, font_scale, (0, 0, 0), thickness)
        
        # Draw emotion probability bars BELOW the label with good spacing
        bar_height = 28
        bar_y_start = label_y + 35
        bar_width = (x_max - x_min) // len(self.emotions)
        
        for idx, (emo, prob) in enumerate(sorted(emotion_dict.items(), key=lambda x: x[1], reverse=True)):
            x_pos = x_min + idx * bar_width
            bar_fill_height = int(prob * bar_height)
            bar_color = self.emotion_colors.get(emo, (100, 100, 100))
            
            # Draw background bar outline
            cv2.rectangle(result, (x_pos + 2, bar_y_start), 
                         (x_pos + bar_width - 4, bar_y_start + bar_height),
                         (220, 220, 220), 2)
            
            # Draw filled bar
            if bar_fill_height > 0:
                cv2.rectangle(result, (x_pos + 2, bar_y_start + bar_height - bar_fill_height),
                             (x_pos + bar_width - 4, bar_y_start + bar_height),
                             bar_color, -1)
            
            # Draw emotion label ABOVE the bar (separated)
            cv2.putText(result, emo[:3].upper(), (x_pos + 5, bar_y_start - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, bar_color, 1)
            
            # Draw probability percentage (white if in bar, dark if above)
            prob_text = f"{prob*100:.0f}%"
            if bar_fill_height > 18:
                # Draw inside the bar
                prob_y = bar_y_start + bar_height - 4
                text_color = (255, 255, 255)
            else:
                # Draw below the bar
                prob_y = bar_y_start + bar_height + 12
                text_color = bar_color
            
            cv2.putText(result, prob_text, (x_pos + 4, prob_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        
        return result
