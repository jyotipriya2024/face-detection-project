# features/training/losses/__init__.py
from .focal_loss import FocalLoss
from .giou_loss import GIoULoss
from .multitask_loss import MultiTaskLoss, LossConfig

__all__ = ["FocalLoss", "GIoULoss", "MultiTaskLoss", "LossConfig"]
