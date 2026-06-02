# features/detection/pipeline.py
"""
End-to-end LightFace-Net detection pipeline.

Wraps backbone → A-FPN → dual head → NMS into a single callable.
Accepts a raw BGR image (numpy) or a pre-processed tensor.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
import torch
import torch.nn as nn
import yaml

from .backbone import LightFaceNet, BackboneConfig
from .fpn import AsymmetricFPN, AFPNConfig
from .head import DualHead, HeadConfig, AnchorGenerator, AnchorConfig, apply_nms, NMSConfig
from shared.bbox_utils import decode_deltas, cxcywh_to_xyxy


# ---------------------------------------------------------------------------
# Fallback face detector — used when LightFaceNet has no trained weights
# ---------------------------------------------------------------------------

def _haar_detect(bgr: np.ndarray, confidence: float = 0.5) -> "List[BoundingBox]":
    """
    Direct Haar-cascade face detection.  Always available via OpenCV.
    Falls back to MediaPipe if installed for higher accuracy.
    Returns List[BoundingBox] — never raises.
    """
    results: List[BoundingBox] = []

    # --- Try MediaPipe first (higher accuracy) ---
    try:
        import mediapipe as mp  # noqa: F401
        face_det = mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=confidence)
        h, w = bgr.shape[:2]
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        mp_result = face_det.process(rgb)
        face_det.close()
        if mp_result.detections:
            for det in mp_result.detections:
                bb = det.location_data.relative_bounding_box
                x1 = max(0, int(bb.xmin * w))
                y1 = max(0, int(bb.ymin * h))
                x2 = min(w, int((bb.xmin + bb.width) * w))
                y2 = min(h, int((bb.ymin + bb.height) * h))
                score = float(det.score[0]) if det.score else 0.9
                if x2 > x1 and y2 > y1:
                    results.append(BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2, score=score))
        return results
    except Exception:
        pass

    # --- Haar cascade (always available) ---
    try:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        haar = cv2.CascadeClassifier(cascade_path)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        # equalizeHist improves detection in varied lighting
        gray = cv2.equalizeHist(gray)
        faces = haar.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=6, minSize=(40, 40),
            flags=cv2.CASCADE_SCALE_IMAGE)
        if len(faces):
            for (x, y, fw, fh) in faces:
                results.append(BoundingBox(
                    x1=float(x), y1=float(y),
                    x2=float(x + fw), y2=float(y + fh),
                    score=0.9))
    except Exception:
        pass

    return results


@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float
    score: float

    def to_dict(self) -> dict:
        return dict(x1=self.x1, y1=self.y1, x2=self.x2, y2=self.y2,
                    score=round(self.score, 4))


@dataclass
class PipelineConfig:
    backbone: BackboneConfig = field(default_factory=BackboneConfig)
    afpn: AFPNConfig = field(default_factory=AFPNConfig)
    head: HeadConfig = field(default_factory=HeadConfig)
    anchor: AnchorConfig = field(default_factory=AnchorConfig)
    nms: NMSConfig = field(default_factory=NMSConfig)
    input_size: tuple = (640, 480)   # (W, H)
    device: str = 'cpu'
    mean: tuple = (0.485, 0.456, 0.406)
    std: tuple = (0.229, 0.224, 0.225)


class DetectionPipeline(nn.Module):
    """
    Full inference pipeline:
        BGR image → pre-process → backbone → A-FPN → head → NMS → BoundingBox list

    Usage:
        pipeline = DetectionPipeline()
        boxes = pipeline.detect(bgr_frame)
    """

    def __init__(self, cfg: PipelineConfig = PipelineConfig()):
        super().__init__()
        self.cfg = cfg
        self.device = torch.device(cfg.device)

        self.backbone = LightFaceNet(cfg.backbone)
        self.afpn = AsymmetricFPN(cfg.afpn)
        self.head = DualHead(cfg.head)
        self.anchor_gen = AnchorGenerator(cfg.anchor)

        self.to(self.device)
        self.eval()

        self._last_fps: float = 0.0
        # Set to True once real trained weights are loaded
        self._is_trained: bool = False
        self._last_anchors: list = []

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, config_path: str) -> "DetectionPipeline":
        with open(config_path) as f:
            raw = yaml.safe_load(f)
        cfg = PipelineConfig(**raw.get('pipeline', {}))
        pipeline = cls(cfg)
        ckpt = raw.get('checkpoint')
        if ckpt and Path(ckpt).exists():
            state = torch.load(ckpt, map_location=cfg.device)
            pipeline.load_state_dict(state, strict=False)
            pipeline._is_trained = True
        return pipeline

    def load_checkpoint(self, path: str) -> None:
        """Load trained weights and mark pipeline as trained."""
        state = torch.load(path, map_location=self.device)
        self.load_state_dict(state.get('model_state', state), strict=False)
        self._is_trained = True

    # ------------------------------------------------------------------
    # Pre / Post processing
    # ------------------------------------------------------------------

    def _preprocess(self, bgr: np.ndarray) -> torch.Tensor:
        W, H = self.cfg.input_size
        rgb = cv2.cvtColor(cv2.resize(bgr, (W, H)), cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(rgb).float().div(255.0).permute(2, 0, 1)
        mean = torch.tensor(self.cfg.mean).view(3, 1, 1)
        std = torch.tensor(self.cfg.std).view(3, 1, 1)
        return ((tensor - mean) / std).unsqueeze(0).to(self.device)

    def _postprocess(self, head_out: dict, orig_shape: tuple
                     ) -> List[BoundingBox]:
        """Decode deltas, concat levels, apply NMS, rescale to original image."""
        orig_h, orig_w = orig_shape[:2]
        inp_w, inp_h = self.cfg.input_size

        all_boxes: List[torch.Tensor] = []
        all_scores: List[torch.Tensor] = []

        feat_shapes = []
        for name in ['F3', 'F4', 'F5']:
            lvl = head_out[name]
            # Recover spatial dims from cls shape: (B, HWn, 1)
            cls = lvl['cls']  # (1, HWn, 1)
            reg = lvl['reg']  # (1, HWn, 4)
            feat_shapes.append(None)   # filled below via anchor count
            all_scores.append(torch.sigmoid(cls[0, :, 0]))
            all_boxes.append(reg[0])   # (HWn, 4) raw deltas

        # Generate anchors — need spatial sizes; estimate from anchor count
        # Anchor shapes are inferred from A-FPN output sizes stored in forward pass
        # (For simplicity we reuse stored feat_shapes set during forward)
        anchors_list = self._last_anchors
        decoded_boxes = [
            cxcywh_to_xyxy(decode_deltas(a, d))
            for a, d in zip(anchors_list, all_boxes)
        ]
        boxes_cat = torch.cat(decoded_boxes, dim=0)
        scores_cat = torch.cat(all_scores, dim=0)

        # Clip to input size
        boxes_cat[:, [0, 2]] = boxes_cat[:, [0, 2]].clamp(0, inp_w)
        boxes_cat[:, [1, 3]] = boxes_cat[:, [1, 3]].clamp(0, inp_h)

        keep = apply_nms(boxes_cat, scores_cat, self.cfg.nms)
        if keep.numel() == 0:
            return []

        kept_boxes = boxes_cat[keep].cpu()
        kept_scores = scores_cat[keep].cpu()

        # Rescale to original image coordinates
        sx, sy = orig_w / inp_w, orig_h / inp_h
        results = []
        for b, s in zip(kept_boxes, kept_scores):
            results.append(BoundingBox(
                x1=float(b[0] * sx), y1=float(b[1] * sy),
                x2=float(b[2] * sx), y2=float(b[3] * sy),
                score=float(s),
            ))
        return results

    # ------------------------------------------------------------------
    # Forward (training mode)
    # ------------------------------------------------------------------

    def forward(self, x: torch.Tensor) -> dict:
        """Raw forward pass used during training."""
        backbone_feats = self.backbone(x)
        fpn_feats = self.afpn(backbone_feats)

        # Store feature shapes for anchor generation
        feat_shapes = [(v.shape[2], v.shape[3]) for v in fpn_feats.values()]
        self._last_anchors = self.anchor_gen.generate_all(feat_shapes, self.device)

        head_out = self.head(fpn_feats)
        return head_out

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    @torch.no_grad()
    def detect(self, bgr: np.ndarray) -> List[BoundingBox]:
        """Full inference on a single BGR frame.

        When trained weights are loaded, uses LightFaceNet + A-FPN pipeline.
        Otherwise falls back to a reliable OpenCV-based detector for demo use.
        """
        t0 = time.perf_counter()
        if self._is_trained:
            tensor = self._preprocess(bgr)
            head_out = self.forward(tensor)
            results = self._postprocess(head_out, bgr.shape)
        else:
            # Use reliable pre-trained detector until LightFaceNet weights are loaded
            results = _haar_detect(bgr)
        self._last_fps = 1.0 / max(time.perf_counter() - t0, 1e-6)
        return results

    @property
    def last_fps(self) -> float:
        return round(self._last_fps, 2)

    def get_performance_metrics(self) -> dict:
        return {
            'fps': self.last_fps,
            'latency_ms': round(1000.0 / max(self._last_fps, 1e-3), 2),
            'device': str(self.device),
        }
