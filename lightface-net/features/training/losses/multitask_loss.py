# features/training/losses/multitask_loss.py
"""
Multi-task loss for LightFace-Net.

L_total = L_cls (Focal) + lambda * L_reg (GIoU)

lambda_reg defaults to 2.0 — up-weights regression relative to classification
to counteract the sparse positive-anchor distribution.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

import torch
import torch.nn as nn

from .focal_loss import FocalLoss
from .giou_loss import GIoULoss


@dataclass
class LossConfig:
    focal_alpha: float = 0.25
    focal_gamma: float = 2.0
    lambda_reg: float = 2.0


class MultiTaskLoss(nn.Module):
    """
    Combined focal classification + GIoU regression loss.

    Args:
        cfg: LossConfig
    """

    def __init__(self, cfg: LossConfig = LossConfig()):
        super().__init__()
        self.focal = FocalLoss(alpha=cfg.focal_alpha, gamma=cfg.focal_gamma)
        self.giou = GIoULoss()
        self.lam = cfg.lambda_reg

    def forward(self, preds: Dict[str, torch.Tensor],
                targets: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """
        Args:
            preds:   {'cls_scores': (N,), 'bbox_coords': (N,4)}
            targets: {'labels': (N,), 'bbox_gt': (N,4)}

        Returns:
            {'total': scalar, 'cls': scalar, 'reg': scalar}
        """
        cls_loss = self.focal(preds['cls_scores'], targets['labels'])
        reg_loss = self.giou(preds['bbox_coords'], targets['bbox_gt'])
        total = cls_loss + self.lam * reg_loss
        return {'total': total, 'cls': cls_loss, 'reg': reg_loss}
