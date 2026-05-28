# features/detection/head/nms.py
"""
Non-Maximum Suppression utilities.
Provides batched NMS and class-agnostic NMS for face detection post-processing.
"""

from __future__ import annotations
from typing import List
from dataclasses import dataclass

import torch


@dataclass
class NMSConfig:
    score_threshold: float = 0.3
    iou_threshold: float = 0.45
    max_detections: int = 300


def box_iou(boxes_a: torch.Tensor, boxes_b: torch.Tensor) -> torch.Tensor:
    """
    Compute IoU between two sets of boxes.
    Boxes are (x1, y1, x2, y2).
    Returns (N, M) IoU matrix.
    """
    area_a = (boxes_a[:, 2] - boxes_a[:, 0]) * (boxes_a[:, 3] - boxes_a[:, 1])
    area_b = (boxes_b[:, 2] - boxes_b[:, 0]) * (boxes_b[:, 3] - boxes_b[:, 1])

    inter_x1 = torch.max(boxes_a[:, None, 0], boxes_b[None, :, 0])
    inter_y1 = torch.max(boxes_a[:, None, 1], boxes_b[None, :, 1])
    inter_x2 = torch.min(boxes_a[:, None, 2], boxes_b[None, :, 2])
    inter_y2 = torch.min(boxes_a[:, None, 3], boxes_b[None, :, 3])

    inter_area = (inter_x2 - inter_x1).clamp(0) * (inter_y2 - inter_y1).clamp(0)
    union = area_a[:, None] + area_b[None, :] - inter_area
    return inter_area / union.clamp(min=1e-6)


def apply_nms(boxes: torch.Tensor, scores: torch.Tensor,
              cfg: NMSConfig = NMSConfig()) -> torch.Tensor:
    """
    Class-agnostic NMS.

    Args:
        boxes:  (N, 4) in (x1, y1, x2, y2)
        scores: (N,)
        cfg:    NMSConfig

    Returns:
        keep: 1-D index tensor of surviving detections (sorted by score desc)
    """
    mask = scores >= cfg.score_threshold
    boxes, scores = boxes[mask], scores[mask]
    if boxes.numel() == 0:
        return torch.empty(0, dtype=torch.long)

    order = scores.argsort(descending=True)
    keep: List[int] = []
    while order.numel() > 0:
        i = order[0].item()
        keep.append(i)
        if order.numel() == 1 or len(keep) >= cfg.max_detections:
            break
        iou = box_iou(boxes[order[1:]], boxes[order[0:1]]).squeeze(1)
        order = order[1:][iou <= cfg.iou_threshold]

    return torch.tensor(keep, dtype=torch.long)
