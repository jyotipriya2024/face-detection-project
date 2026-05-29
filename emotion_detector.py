"""
Emotion Detection Module
Detects emotional expressions using deep learning.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional


class EmotionDetector:
    """
    Detects emotions from facial expressions using CNN.
    Supports: happy, sad, angry, surprised, fear, disgust, neutral
    """
    
    def __init__(self, config: Optional[Dict] = None):
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
        self.config = {
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
        if config:
            self.config.update(config)
        self.emotion_history = {}
        self.history_idle = {}
        self.feature_history = {}
        
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
    
    def detect_emotion(self, face_image: np.ndarray, face_id: Optional[int] = None) -> Dict[str, float]:
        """
        Detect emotion from face image using feature analysis.
        
        Args:
            face_image: Cropped face image
            
        Returns:
            Dictionary with emotion probabilities
        """
        if face_image is None or face_image.size == 0:
            return {emotion: 1.0/len(self.emotions) for emotion in self.emotions}
        min_face_px = int(self.config.get('min_face_px', 40))
        if (face_image.shape[0] < min_face_px or
            face_image.shape[1] < min_face_px):
            return {emotion: 1.0/len(self.emotions) for emotion in self.emotions}
        
        try:
            # Use feature-based emotion detection
            emotion_dict = self._detect_emotion_features(face_image, face_id)
            return self._smooth_emotion(emotion_dict, face_id)
        except Exception as e:
            print(f"Error in emotion detection: {e}")
            return {emotion: 1.0/len(self.emotions) for emotion in self.emotions}

    def prune_history(self, active_ids: Optional[set] = None):
        if not self.emotion_history:
            return
        if active_ids is None:
            active_ids = set()
        for face_id in list(self.emotion_history.keys()):
            if face_id in active_ids:
                self.history_idle[face_id] = 0
                continue
            self.history_idle[face_id] = self.history_idle.get(face_id, 0) + 1
            if self.history_idle[face_id] > self.config['history_max_idle']:
                self.emotion_history.pop(face_id, None)
                self.history_idle.pop(face_id, None)
    
    def _detect_emotion_features(self, face_image: np.ndarray, face_id: Optional[int]) -> Dict[str, float]:
        """
        Detect emotion using relative feature comparisons rather than absolute thresholds.
        More robust for varying lighting and real webcam conditions.
        """
        try:
            # Preprocess
            gray_raw = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            input_size = int(self.config['input_size'])
            gray_raw = cv2.resize(gray_raw, (input_size, input_size))
            gray = cv2.GaussianBlur(gray_raw, (3, 3), 0)
            if self.config['use_clahe']:
                gray = self._apply_clahe(gray)
            if self.config['gamma'] and self.config['gamma'] != 1.0:
                gray = self._apply_gamma(gray, float(self.config['gamma']))
            
            # Extract core features (use raw for brightness/contrast stability)
            brightness = np.mean(gray_raw) / 255.0
            contrast = np.std(gray_raw) / 255.0
            
            # Edge detection
            edges = cv2.Canny(gray, 30, 100)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Saturation from HSV
            hsv = cv2.cvtColor(face_image, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:, :, 1]) / 255.0
            
            # Regional brightness for droopy/raised features
            h_step = input_size // 3
            upper_brightness = np.mean(gray[:h_step, :]) / 255.0
            lower_brightness = np.mean(gray[2*h_step:, :]) / 255.0
            brightness_diff = upper_brightness - lower_brightness

            # Regional edge densities
            upper_edges = edges[:h_step, :]
            mid_edges = edges[h_step:2*h_step, :]
            lower_edges = edges[2*h_step:, :]
            upper_edge_density = np.sum(upper_edges > 0) / upper_edges.size
            mid_edge_density = np.sum(mid_edges > 0) / mid_edges.size
            lower_edge_density = np.sum(lower_edges > 0) / lower_edges.size

            # Regional contrast (mouth vs eyes)
            upper_contrast = np.std(gray[:h_step, :]) / 255.0
            lower_contrast = np.std(gray[2*h_step:, :]) / 255.0

            # Texture variance for expression intensity
            lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            lap_var_norm = min(lap_var / 150.0, 1.0)

            features = {
                'brightness': brightness,
                'contrast': contrast,
                'saturation': saturation,
                'edge_density': edge_density,
                'brightness_diff': brightness_diff,
                'upper_brightness': upper_brightness,
                'upper_edge_density': upper_edge_density,
                'mid_edge_density': mid_edge_density,
                'lower_edge_density': lower_edge_density,
                'upper_contrast': upper_contrast,
                'lower_contrast': lower_contrast,
                'lap_var_norm': lap_var_norm,
            }
            features = self._apply_feature_normalization(features, face_id)
            brightness = features['brightness']
            contrast = features['contrast']
            saturation = features['saturation']
            edge_density = features['edge_density']
            brightness_diff = features['brightness_diff']
            upper_brightness = features['upper_brightness']
            upper_edge_density = features['upper_edge_density']
            mid_edge_density = features['mid_edge_density']
            lower_edge_density = features['lower_edge_density']
            upper_contrast = features['upper_contrast']
            lower_contrast = features['lower_contrast']
            lap_var_norm = features['lap_var_norm']
            
            scores = {}
            
            # Base scores - each emotion gets a baseline
            # Then we adjust based on how well features match
            
            # HAPPY: Brightness and saturation above average, mouth edges/contrast high
            happy_brightness_bonus = max(0, brightness - 0.50) / 0.50  # Favors brighter
            happy_saturation_bonus = max(0, saturation - 0.45) / 0.55  # Favors more saturated
            happy_smooth_bonus = max(0, 1 - edge_density / 0.30)  # Favors smooth
            happy_mouth_bonus = max(0, lower_edge_density - 0.08) / 0.20
            happy_mouth_contrast = max(0, lower_contrast - 0.12) / 0.25
            scores['happy'] = (0.2 + 
                              happy_brightness_bonus * 0.35 + 
                              happy_saturation_bonus * 0.30 + 
                              happy_smooth_bonus * 0.05 +
                              happy_mouth_bonus * 0.15 +
                              happy_mouth_contrast * 0.15)
            
            # SAD: Lower brightness and saturation, droopy (upper > lower), low mouth contrast
            sad_dark_bonus = max(0, 1 - brightness / 0.70)  # Favors darker
            sad_desaturate_bonus = max(0, 1 - saturation / 0.65)  # Favors desaturated
            sad_droop_bonus = max(0, brightness_diff * 2)  # Favors upper > lower
            sad_low_mouth = max(0, 0.14 - lower_contrast) / 0.14
            scores['sad'] = (0.15 + 
                            sad_dark_bonus * 0.35 + 
                            sad_desaturate_bonus * 0.30 + 
                            sad_droop_bonus * 0.20 +
                            sad_low_mouth * 0.15)
            
            # ANGRY: High contrast + many edges + tension in upper face
            angry_contrast_bonus = max(0, contrast - 0.20) / 0.50  # Favors high contrast
            angry_edges_bonus = max(0, edge_density - 0.15) / 0.35  # Favors edges
            angry_upper_bonus = max(0, upper_edge_density - 0.18) / 0.35
            angry_tension_bonus = lap_var_norm
            scores['angry'] = (0.15 + 
                              angry_contrast_bonus * 0.35 + 
                              angry_edges_bonus * 0.30 +
                              angry_upper_bonus * 0.20 +
                              angry_tension_bonus * 0.15)
            
            # SURPRISED: Very bright + open eyes and mouth
            surprised_brightness_bonus = max(0, brightness - 0.65) / 0.35  # Favors very bright
            surprised_saturation_bonus = max(0, saturation - 0.55) / 0.45  # Favors high sat
            surprised_upper_bonus = max(0, upper_brightness - 0.65) / 0.35  # Bright eyes
            surprised_mouth_bonus = max(0, lower_edge_density - 0.12) / 0.25
            scores['surprised'] = (0.15 + 
                                  surprised_brightness_bonus * 0.35 + 
                                  surprised_saturation_bonus * 0.30 + 
                                  surprised_upper_bonus * 0.15 +
                                  surprised_mouth_bonus * 0.15)
            
            # FEAR: Raised eyebrows + variable expression + moderate tension
            fear_eyes_bonus = max(0, upper_brightness - 0.55) / 0.45  # Bright upper
            fear_variable_bonus = abs(brightness_diff) / 0.30  # Variable brightness
            fear_edges_bonus = max(0, edge_density - 0.15) / 0.30  # Some edges
            fear_tension_bonus = lap_var_norm * 0.8
            scores['fear'] = (0.15 + 
                             fear_eyes_bonus * 0.35 + 
                             fear_variable_bonus * 0.30 + 
                             fear_edges_bonus * 0.10 +
                             fear_tension_bonus * 0.10)
            
            # DISGUST: Very desaturated with mid-face tension
            disgust_desaturate_bonus = max(0, 1 - saturation / 0.50)  # Very desaturated
            disgust_dark_bonus = max(0, 1 - brightness / 0.70)  # Darker
            disgust_mid_bonus = max(0, mid_edge_density - 0.14) / 0.30
            scores['disgust'] = (0.15 + 
                                disgust_desaturate_bonus * 0.60 + 
                                disgust_dark_bonus * 0.15 +
                                disgust_mid_bonus * 0.10)
            
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

    def _apply_clahe(self, gray: np.ndarray) -> np.ndarray:
        clahe = cv2.createCLAHE(
            clipLimit=self.config['clahe_clip_limit'],
            tileGridSize=self.config['clahe_grid_size']
        )
        return clahe.apply(gray)

    def _apply_gamma(self, gray: np.ndarray, gamma: float) -> np.ndarray:
        inv_gamma = 1.0 / max(gamma, 1e-6)
        table = (np.linspace(0, 1, 256) ** inv_gamma) * 255
        return cv2.LUT(gray, table.astype(np.uint8))

    def _smooth_emotion(self, emotion_dict: Dict[str, float], face_id: Optional[int]) -> Dict[str, float]:
        if face_id is None or self.config['smoothing_alpha'] <= 0:
            return emotion_dict
        alpha = float(self.config['smoothing_alpha'])
        prev = self.emotion_history.get(face_id)
        if prev:
            smoothed = {
                emo: (alpha * emotion_dict.get(emo, 0.0)) + ((1.0 - alpha) * prev.get(emo, 0.0))
                for emo in self.emotions
            }
            total = sum(smoothed.values())
            if total > 0:
                smoothed = {emo: val / total for emo, val in smoothed.items()}
        else:
            smoothed = emotion_dict
        self.emotion_history[face_id] = smoothed
        self.history_idle[face_id] = 0
        return smoothed

    def _apply_feature_normalization(self, features: Dict[str, float],
                                     face_id: Optional[int]) -> Dict[str, float]:
        if face_id is None:
            return features
        alpha = float(self.config['feature_alpha'])
        delta_weight = float(self.config['delta_weight'])
        history = self.feature_history.get(face_id)
        if history is None:
            self.feature_history[face_id] = features.copy()
            return features
        updated = {}
        adjusted = {}
        for key, value in features.items():
            prev = history.get(key, value)
            ema = (alpha * value) + ((1.0 - alpha) * prev)
            updated[key] = ema
            adjusted[key] = value + delta_weight * (value - ema)
        self.feature_history[face_id] = updated
        return adjusted
    
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
