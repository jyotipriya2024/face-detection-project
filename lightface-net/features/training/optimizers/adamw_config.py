# features/training/optimizers/adamw_config.py
"""
AdamW optimizer + cosine annealing LR scheduler factory.

All hyperparameters are driven from infrastructure/config/training_config.yaml.
The function returns (optimizer, scheduler) ready for the training loop.
"""

from __future__ import annotations
from dataclasses import dataclass

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR, SequentialLR

from .warmup import LinearWarmupScheduler


@dataclass
class OptimizerConfig:
    lr: float = 1e-3
    weight_decay: float = 5e-4
    betas: tuple = (0.9, 0.999)
    eps: float = 1e-8
    warmup_epochs: int = 5
    total_epochs: int = 120
    warmup_start_lr: float = 1e-6
    eta_min: float = 1e-6          # cosine floor LR


def build_optimizer_and_scheduler(
    model: nn.Module,
    steps_per_epoch: int,
    cfg: OptimizerConfig = OptimizerConfig(),
) -> tuple[AdamW, SequentialLR]:
    """
    Build AdamW + (linear warmup → cosine annealing) scheduler pair.

    Batch norm / bias parameters are excluded from weight decay.

    Returns:
        (optimizer, scheduler)  — scheduler operates per-epoch.
    """
    # Separate decay / no-decay param groups
    decay_params, no_decay_params = [], []
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        if param.ndim < 2 or 'bias' in name or 'bn' in name:
            no_decay_params.append(param)
        else:
            decay_params.append(param)

    param_groups = [
        {'params': decay_params,    'weight_decay': cfg.weight_decay},
        {'params': no_decay_params, 'weight_decay': 0.0},
    ]
    optimizer = AdamW(param_groups, lr=cfg.lr,
                      betas=cfg.betas, eps=cfg.eps)

    warmup_scheduler = LinearWarmupScheduler(
        optimizer,
        warmup_steps=cfg.warmup_epochs,
        warmup_start_lr=cfg.warmup_start_lr,
    )
    cosine_scheduler = CosineAnnealingLR(
        optimizer,
        T_max=cfg.total_epochs - cfg.warmup_epochs,
        eta_min=cfg.eta_min,
    )
    scheduler = SequentialLR(
        optimizer,
        schedulers=[warmup_scheduler, cosine_scheduler],
        milestones=[cfg.warmup_epochs],
    )
    return optimizer, scheduler
