# shared/bbox_utils.py
"""
Bounding-box utility functions.
Pure math — zero imports from model or dataset code.

Coordinate conventions:
  - xyxy: (x1, y1, x2, y2)  — top-left / bottom-right corners
  - cxcywh: (cx, cy, w, h)  — centre + size
"""

from __future__ import annotations
import torch
import numpy as np


# -------------------------------------------------------------------------
# Format conversion
# -------------------------------------------------------------------------

def xyxy_to_cxcywh(boxes: torch.Tensor) -> torch.Tensor:
    """(x1, y1, x2, y2) → (cx, cy, w, h)"""
    x1, y1, x2, y2 = boxes.unbind(-1)
    return torch.stack([(x1 + x2) / 2, (y1 + y2) / 2,
                         x2 - x1, y2 - y1], dim=-1)


def cxcywh_to_xyxy(boxes: torch.Tensor) -> torch.Tensor:
    """(cx, cy, w, h) → (x1, y1, x2, y2)"""
    cx, cy, w, h = boxes.unbind(-1)
    return torch.stack([cx - w / 2, cy - h / 2,
                         cx + w / 2, cy + h / 2], dim=-1)


# -------------------------------------------------------------------------
# Box encoding / decoding (delta regression)
# -------------------------------------------------------------------------

def encode_deltas(anchors: torch.Tensor,
                  gt_boxes: torch.Tensor,
                  weights: tuple = (1.0, 1.0, 1.0, 1.0)) -> torch.Tensor:
    """
    Encode ground-truth boxes as delta offsets relative to anchors.
    Both inputs are (N, 4) in cxcywh format.
    """
    wx, wy, ww, wh = weights
    ex = (gt_boxes[:, 0] - anchors[:, 0]) / anchors[:, 2] * wx
    ey = (gt_boxes[:, 1] - anchors[:, 1]) / anchors[:, 3] * wy
    ew = torch.log(gt_boxes[:, 2] / anchors[:, 2].clamp(min=1e-6)) * ww
    eh = torch.log(gt_boxes[:, 3] / anchors[:, 3].clamp(min=1e-6)) * wh
    return torch.stack([ex, ey, ew, eh], dim=-1)


def decode_deltas(anchors: torch.Tensor,
                  deltas: torch.Tensor,
                  weights: tuple = (1.0, 1.0, 1.0, 1.0),
                  max_shape: tuple | None = None) -> torch.Tensor:
    """
    Decode predicted deltas back to (cx, cy, w, h) boxes.
    Both anchors and output are in cxcywh format.
    """
    wx, wy, ww, wh = weights
    dx, dy, dw, dh = deltas[:, 0], deltas[:, 1], deltas[:, 2], deltas[:, 3]
    # Clamp to prevent exp overflow
    dw = dw.clamp(max=4.0)
    dh = dh.clamp(max=4.0)

    cx = anchors[:, 0] + dx / wx * anchors[:, 2]
    cy = anchors[:, 1] + dy / wy * anchors[:, 3]
    w  = anchors[:, 2] * torch.exp(dw / ww)
    h  = anchors[:, 3] * torch.exp(dh / wh)
    return torch.stack([cx, cy, w, h], dim=-1)


# -------------------------------------------------------------------------
# IoU / GIoU
# -------------------------------------------------------------------------

def box_iou_np(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
    """Vectorised IoU in NumPy. boxes are (N,4) and (M,4) in xyxy."""
    area_a = (boxes_a[:, 2] - boxes_a[:, 0]) * (boxes_a[:, 3] - boxes_a[:, 1])
    area_b = (boxes_b[:, 2] - boxes_b[:, 0]) * (boxes_b[:, 3] - boxes_b[:, 1])
    ix1 = np.maximum(boxes_a[:, None, 0], boxes_b[None, :, 0])
    iy1 = np.maximum(boxes_a[:, None, 1], boxes_b[None, :, 1])
    ix2 = np.minimum(boxes_a[:, None, 2], boxes_b[None, :, 2])
    iy2 = np.minimum(boxes_a[:, None, 3], boxes_b[None, :, 3])
    inter = np.maximum(0, ix2 - ix1) * np.maximum(0, iy2 - iy1)
    union = area_a[:, None] + area_b[None, :] - inter
    return inter / np.maximum(union, 1e-6)
