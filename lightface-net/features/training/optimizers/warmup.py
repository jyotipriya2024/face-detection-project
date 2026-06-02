# features/training/optimizers/warmup.py
"""
Linear warmup learning-rate scheduler.

Linearly scales LR from lr_start to base_lr over warmup_epochs,
then hands off to a downstream scheduler (e.g. CosineAnnealingLR).
"""

from __future__ import annotations
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler


class LinearWarmupScheduler(_LRScheduler):
    """
    Linearly increase LR from warmup_start_lr to base_lr over warmup_steps.

    Typically wrapped around a cosine decay scheduler using
    torch.optim.lr_scheduler.SequentialLR.

    Args:
        optimizer:       The optimizer whose LR is managed.
        warmup_steps:    Number of gradient steps to warm up over.
        warmup_start_lr: Initial (tiny) LR at step 0.
        last_epoch:      For resuming mid-warmup.
    """

    def __init__(self, optimizer: Optimizer, warmup_steps: int,
                 warmup_start_lr: float = 1e-6, last_epoch: int = -1):
        self.warmup_steps = warmup_steps
        self.warmup_start_lr = warmup_start_lr
        super().__init__(optimizer, last_epoch)

    def get_lr(self) -> list[float]:
        step = self.last_epoch + 1
        if step >= self.warmup_steps:
            return self.base_lrs
        ratio = step / self.warmup_steps
        return [
            self.warmup_start_lr + ratio * (base - self.warmup_start_lr)
            for base in self.base_lrs
        ]
