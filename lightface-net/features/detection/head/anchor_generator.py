# features/detection/head/anchor_generator.py
"""
Face-specific anchor generator.

Anchors are designed for faces:
  - P3 (stride 8):  small faces  8–32 px
  - P4 (stride 16): medium faces 32–128 px
  - P5 (stride 32): large faces  128–512 px
Aspect ratios biased toward portrait faces (taller than wide).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import torch


@dataclass
class AnchorConfig:
    strides: List[int] = field(default_factory=lambda: [8, 16, 32])
    base_sizes: List[List[int]] = field(default_factory=lambda: [
        [16, 32],        # P3 anchors (px)
        [64, 128],       # P4 anchors
        [256, 512],      # P5 anchors
    ])
    aspect_ratios: List[float] = field(default_factory=lambda: [1.0, 1.5])
    # 1.0 = square; 1.5 = portrait (h/w = 1.5) — common for faces


class AnchorGenerator:
    """
    Generates anchor boxes (cx, cy, w, h) for a given feature map size.

    All coordinates are in the *image* pixel space.
    """

    def __init__(self, cfg: AnchorConfig = AnchorConfig()):
        self.cfg = cfg
        self._base_anchors: dict[int, torch.Tensor] = {}
        for stride, sizes in zip(cfg.strides, cfg.base_sizes):
            self._base_anchors[stride] = self._make_base_anchors(sizes,
                                                                  cfg.aspect_ratios)

    @staticmethod
    def _make_base_anchors(sizes: List[int],
                           ratios: List[float]) -> torch.Tensor:
        """Return (N_a, 4) tensor of (cx=0, cy=0, w, h) base anchors."""
        anchors = []
        for s in sizes:
            for r in ratios:
                w = s
                h = s * r
                anchors.append([0.0, 0.0, w, h])
        return torch.tensor(anchors, dtype=torch.float32)

    def generate(self, feat_h: int, feat_w: int, stride: int,
                 device: torch.device = torch.device('cpu')) -> torch.Tensor:
        """
        Generate all anchors for one feature level.

        Returns: (feat_h * feat_w * n_anchors, 4) — (cx, cy, w, h)
        """
        base = self._base_anchors[stride].to(device)   # (n_a, 4)
        shifts_x = (torch.arange(feat_w, device=device) + 0.5) * stride
        shifts_y = (torch.arange(feat_h, device=device) + 0.5) * stride
        grid_y, grid_x = torch.meshgrid(shifts_y, shifts_x, indexing='ij')
        shifts = torch.stack([grid_x.flatten(), grid_y.flatten(),
                               torch.zeros(feat_h * feat_w, device=device),
                               torch.zeros(feat_h * feat_w, device=device)],
                              dim=-1)                   # (HW, 4)
        anchors = (shifts[:, None, :] + base[None, :, :]).reshape(-1, 4)
        return anchors  # (HW * n_a, 4) in (cx, cy, w, h)

    def generate_all(self, feature_shapes: List[Tuple[int, int]],
                     device: torch.device = torch.device('cpu')
                     ) -> List[torch.Tensor]:
        """Generate anchors for all feature levels (F3, F4, F5)."""
        return [
            self.generate(h, w, s, device)
            for (h, w), s in zip(feature_shapes, self.cfg.strides)
        ]
