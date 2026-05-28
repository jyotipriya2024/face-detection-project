# features/training/losses/giou_loss.py
"""
Generalized Intersection-over-Union (GIoU) regression loss.

GIoU = IoU - (C - A∪B) / C
where C is the area of the smallest enclosing box.

GIoU loss = 1 - GIoU  ∈ [-1, 2] but practically [0, 2].

Reference: Rezatofighi et al., "Generalized Intersection over Union", CVPR 2019.
"""

from __future__ import annotations
import torch
import torch.nn as nn


class GIoULoss(nn.Module):
    """
    Generalized IoU bounding-box regression loss.

    Args:
        reduction: 'mean' | 'sum' | 'none'
    """

    def __init__(self, reduction: str = 'mean'):
        super().__init__()
        self.reduction = reduction

    def forward(self, pred_boxes: torch.Tensor,
                target_boxes: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pred_boxes:   (N, 4) in (x1, y1, x2, y2)
            target_boxes: (N, 4) in (x1, y1, x2, y2)
        """
        pred_x1, pred_y1, pred_x2, pred_y2 = pred_boxes.unbind(-1)
        tgt_x1,  tgt_y1,  tgt_x2,  tgt_y2  = target_boxes.unbind(-1)

        # Intersection
        inter_x1 = torch.max(pred_x1, tgt_x1)
        inter_y1 = torch.max(pred_y1, tgt_y1)
        inter_x2 = torch.min(pred_x2, tgt_x2)
        inter_y2 = torch.min(pred_y2, tgt_y2)
        inter_w = (inter_x2 - inter_x1).clamp(0)
        inter_h = (inter_y2 - inter_y1).clamp(0)
        inter_area = inter_w * inter_h

        # Union
        pred_area = (pred_x2 - pred_x1).clamp(0) * (pred_y2 - pred_y1).clamp(0)
        tgt_area  = (tgt_x2  - tgt_x1).clamp(0)  * (tgt_y2  - tgt_y1).clamp(0)
        union_area = pred_area + tgt_area - inter_area

        iou = inter_area / union_area.clamp(min=1e-6)

        # Enclosing box
        enc_x1 = torch.min(pred_x1, tgt_x1)
        enc_y1 = torch.min(pred_y1, tgt_y1)
        enc_x2 = torch.max(pred_x2, tgt_x2)
        enc_y2 = torch.max(pred_y2, tgt_y2)
        enc_area = ((enc_x2 - enc_x1) * (enc_y2 - enc_y1)).clamp(min=1e-6)

        giou = iou - (enc_area - union_area) / enc_area
        loss = 1.0 - giou

        if self.reduction == 'mean':
            return loss.mean()
        if self.reduction == 'sum':
            return loss.sum()
        return loss
