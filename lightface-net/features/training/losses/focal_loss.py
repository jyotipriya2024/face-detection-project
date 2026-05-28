# features/training/losses/focal_loss.py
"""
Focal Loss for binary face/background classification.

FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)

Resolves the extreme class imbalance (~1000 background anchors per face anchor)
by down-weighting the loss assigned to well-classified easy negatives.

Reference: Lin et al., "Focal Loss for Dense Object Detection", ICCV 2017.
"""

from __future__ import annotations
import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """
    Binary focal loss (face vs background).

    Args:
        alpha: Weighting factor for the rare (positive) class. Default 0.25.
        gamma: Focusing exponent. Default 2.0.
        reduction: 'mean' | 'sum' | 'none'
    """

    def __init__(self, alpha: float = 0.25, gamma: float = 2.0,
                 reduction: str = 'mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, pred_logits: torch.Tensor,
                targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred_logits: (N,) or (N,1) — raw scores (before sigmoid)
            targets:     (N,) — binary labels {0, 1}
        """
        pred_logits = pred_logits.view(-1)
        targets = targets.view(-1).float()

        bce = F.binary_cross_entropy_with_logits(
            pred_logits, targets, reduction='none')
        p_t = torch.exp(-bce)                        # = sigmoid(logit*label)
        alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        focal_weight = alpha_t * (1 - p_t) ** self.gamma
        loss = focal_weight * bce

        if self.reduction == 'mean':
            return loss.mean()
        if self.reduction == 'sum':
            return loss.sum()
        return loss
