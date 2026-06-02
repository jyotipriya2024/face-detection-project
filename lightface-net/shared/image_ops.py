# shared/image_ops.py
"""
Stateless image pre/post-processing helpers.
Pure functions — no model or dataset imports.
"""

from __future__ import annotations
from typing import Tuple

import cv2
import numpy as np
import torch

from .constants import IMAGENET_MEAN, IMAGENET_STD


def bgr_to_tensor(bgr: np.ndarray,
                  target_size: Tuple[int, int] = (640, 480),
                  mean: Tuple[float, ...] = IMAGENET_MEAN,
                  std: Tuple[float, ...] = IMAGENET_STD) -> torch.Tensor:
    """
    BGR uint8 (H,W,3) → normalised float tensor (1,3,H,W) ready for inference.

    Args:
        bgr:         Input frame in BGR (OpenCV) format.
        target_size: (W, H) to resize to.
        mean, std:   Normalisation constants.

    Returns:
        (1, 3, target_H, target_W) float32 tensor.
    """
    rgb = cv2.cvtColor(cv2.resize(bgr, target_size), cv2.COLOR_BGR2RGB)
    tensor = torch.from_numpy(rgb).float().div(255.0)   # (H, W, 3)
    _mean = torch.tensor(mean).view(1, 1, 3)
    _std  = torch.tensor(std).view(1, 1, 3)
    tensor = (tensor - _mean) / _std
    return tensor.permute(2, 0, 1).unsqueeze(0)         # (1, 3, H, W)


def tensor_to_bgr(tensor: torch.Tensor,
                  mean: Tuple[float, ...] = IMAGENET_MEAN,
                  std: Tuple[float, ...] = IMAGENET_STD) -> np.ndarray:
    """
    Inverse of bgr_to_tensor: (1,3,H,W) or (3,H,W) → BGR uint8.
    """
    if tensor.dim() == 4:
        tensor = tensor.squeeze(0)
    _mean = torch.tensor(mean).view(3, 1, 1)
    _std  = torch.tensor(std).view(3, 1, 1)
    rgb = (tensor * _std + _mean).clamp(0, 1)
    rgb_np = (rgb.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    return cv2.cvtColor(rgb_np, cv2.COLOR_RGB2BGR)


def resize_with_aspect(bgr: np.ndarray,
                        max_dim: int = 640) -> Tuple[np.ndarray, float]:
    """
    Resize image so the longer side equals max_dim, preserving aspect ratio.

    Returns:
        (resized_image, scale_factor)
    """
    h, w = bgr.shape[:2]
    scale = max_dim / max(h, w)
    if scale < 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        bgr = cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    else:
        scale = 1.0
    return bgr, scale
