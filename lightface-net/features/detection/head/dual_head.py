# features/detection/head/dual_head.py
"""
Dual detection head: parallel classification + bounding-box regression.

For each FPN level a shared convolution stack is applied, then split into:
  - cls_head  → face/background logits  (B, H*W*n_anchors, 1)
  - reg_head  → box deltas (dx, dy, dw, dh)  (B, H*W*n_anchors, 4)

A single DualHead instance is shared across all FPN levels (weights tied).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import torch
import torch.nn as nn


@dataclass
class HeadConfig:
    in_channels: int = 256       # A-FPN output channels
    num_anchors: int = 4         # anchors per location (2 sizes × 2 ratios)
    num_convs: int = 4           # shared conv stack depth


class DualHead(nn.Module):
    """
    Shared-weight classification + regression head applied to each FPN level.

    Output layout per level:
        cls_logits: (B, H*W*num_anchors, 1)
        bbox_deltas: (B, H*W*num_anchors, 4)
    """

    def __init__(self, cfg: HeadConfig = HeadConfig()):
        super().__init__()
        C = cfg.in_channels
        n = cfg.num_anchors

        self.shared = nn.Sequential(
            *[block for _ in range(cfg.num_convs)
              for block in (
                  nn.Conv2d(C, C, 3, padding=1, bias=False),
                  nn.GroupNorm(32, C),
                  nn.ReLU(inplace=True),
              )]
        )

        self.cls_conv = nn.Conv2d(C, n * 1, 3, padding=1)
        self.reg_conv = nn.Conv2d(C, n * 4, 3, padding=1)

        # Focal-loss-friendly initialization: bias → -log((1-pi)/pi)
        prior_prob = 0.01
        nn.init.constant_(self.cls_conv.bias,
                          -torch.tensor(prior_prob).log1p() +
                          torch.tensor(1 - prior_prob).log())

    def forward_single(self, feat: torch.Tensor
                       ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Process one FPN level. Returns (cls_logits, bbox_deltas)."""
        B, C, H, W = feat.shape
        shared = self.shared(feat)
        n = self.cls_conv.out_channels // 1

        cls = self.cls_conv(shared)                 # (B, n, H, W)
        reg = self.reg_conv(shared)                 # (B, 4n, H, W)

        cls = cls.permute(0, 2, 3, 1).reshape(B, -1, 1)   # (B, HWn, 1)
        reg = reg.permute(0, 2, 3, 1).reshape(B, -1, 4)   # (B, HWn, 4)
        return cls, reg

    def forward(self, fpn_features: Dict[str, torch.Tensor]
                ) -> Dict[str, Dict[str, torch.Tensor]]:
        """
        Apply head to all FPN levels.

        Returns:
            {
              'F3': {'cls': ..., 'reg': ...},
              'F4': {'cls': ..., 'reg': ...},
              'F5': {'cls': ..., 'reg': ...},
            }
        """
        out = {}
        for name, feat in fpn_features.items():
            cls_logits, bbox_deltas = self.forward_single(feat)
            out[name] = {'cls': cls_logits, 'reg': bbox_deltas}
        return out
