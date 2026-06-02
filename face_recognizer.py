"""
Face Recognition Module
Recognizes and identifies faces using embeddings and matching.
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
import os
from pathlib import Path


class FaceRecognizer:
    """
    Recognizes faces using embedding vectors and similarity matching.
    Supports face enrollment and identification.
    """
    
    def __init__(self, embedding_dim: int = 128, similarity_threshold: float = 0.6):
        """
        Initialize face recognizer.
        
        Args:
            embedding_dim: Dimension of face embeddings
            similarity_threshold: Threshold for face matching (0-1)
        """
        self.embedding_dim = embedding_dim
        self.similarity_threshold = similarity_threshold
        self.enrolled_faces = {}  # {person_name: [embeddings]}
        self.face_database_path = Path("face_database")
        self.face_database_path.mkdir(exist_ok=True)
        self._load_database()
    
    def _load_database(self):
        """Load enrolled faces from database."""
        try:
            db_file = self.face_database_path / "enrollments.json"
            if db_file.exists():
                with open(db_file, 'r') as f:
                    data = json.load(f)
                    self.enrolled_faces = data
                print(f"Loaded {len(self.enrolled_faces)} enrolled faces")
        except Exception as e:
            print(f"Could not load face database: {e}")
    
    def _save_database(self):
        """Save enrolled faces to database."""
        try:
            db_file = self.face_database_path / "enrollments.json"
            with open(db_file, 'w') as f:
                json.dump(self.enrolled_faces, f, indent=2)
        except Exception as e:
            print(f"Could not save face database: {e}")
    
    def generate_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Generate embedding vector for a face.
        
        Args:
            face_image: Cropped face image
            
        Returns:
            Embedding vector (1D array)
        """
        # Placeholder: In production, use:
        # - FaceNet
        # - VGGFace2
        # - ArcFace
        # - DeepFace
        
        try:
            # Simple feature extraction using OpenCV (histogram)
            # In production, replace with deep learning model
            
            # Resize to standard size
            face = cv2.resize(face_image, (224, 224))
            
            # Convert to grayscale
            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            
            # Compute histogram
            hist = cv2.calcHist([gray], [0], None, [self.embedding_dim], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()
            
            # Pad or trim to embedding_dim
            if len(hist) < self.embedding_dim:
                hist = np.pad(hist, (0, self.embedding_dim - len(hist)))
            else:
                hist = hist[:self.embedding_dim]
            
            return hist
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return np.random.randn(self.embedding_dim)
    
    def enroll_face(self, person_name: str, face_images: List[np.ndarray]) -> bool:
        """
        Enroll a person with multiple face images.
        
        Args:
            person_name: Name of the person
            face_images: List of face images for enrollment
            
        Returns:
            Success status
        """
        try:
            embeddings = []
            for face_image in face_images:
                embedding = self.generate_embedding(face_image)
                embeddings.append(embedding.tolist())
            
            self.enrolled_faces[person_name] = embeddings
            self._save_database()
            print(f"Enrolled {person_name} with {len(embeddings)} faces")
            return True
        except Exception as e:
            print(f"Error enrolling face: {e}")
            return False
    
    def recognize_face(self, face_image: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Recognize a face and find matching enrolled person.
        
        Args:
            face_image: Face image to recognize
            
        Returns:
            Tuple of (person_name, confidence) or (None, 0)
        """
        if not self.enrolled_faces:
            return None, 0.0
        
        query_embedding = self.generate_embedding(face_image)
        
        best_match = None
        best_score = 0.0
        
        for person_name, embeddings in self.enrolled_faces.items():
            # Compute average similarity to all embeddings of this person
            similarities = []
            for embedding in embeddings:
                similarity = self._compute_similarity(query_embedding, np.array(embedding))
                similarities.append(similarity)
            
            avg_similarity = np.mean(similarities)
            
            if avg_similarity > best_score and avg_similarity >= self.similarity_threshold:
                best_match = person_name
                best_score = avg_similarity
        
        return best_match, best_score
    
    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        emb1 = emb1 / norm1
        emb2 = emb2 / norm2
        
        similarity = np.dot(emb1, emb2)
        # Normalize to 0-1 range
        similarity = (similarity + 1) / 2
        
        return float(similarity)
    
    def delete_person(self, person_name: str) -> bool:
        """Delete enrolled person from database."""
        if person_name in self.enrolled_faces:
            del self.enrolled_faces[person_name]
            self._save_database()
            return True
        return False
    
    def draw_recognition(self, image: np.ndarray, face_bbox: Tuple[int, int, int, int],
                        person_name: Optional[str], confidence: float) -> np.ndarray:
        """
        Draw recognition result on image.
        
        Args:
            image: Input image
            face_bbox: Face bounding box
            person_name: Recognized person name or None
            confidence: Recognition confidence
            
        Returns:
            Image with drawn recognition
        """
        result = image.copy()
        x_min, y_min, x_max, y_max = face_bbox
        
        if person_name:
            color = (0, 255, 0)  # Green for recognized
            label = f"{person_name} ({confidence:.2f})"
        else:
            color = (0, 0, 255)  # Red for unknown
            label = "Unknown"
        
        cv2.rectangle(result, (x_min, y_min), (x_max, y_max), color, 2)
        cv2.putText(result, label, (x_min, y_min - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        return result
    
    def list_enrolled_people(self) -> List[str]:
        """Get list of all enrolled people."""
        return list(self.enrolled_faces.keys())
