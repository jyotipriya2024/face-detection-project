# features/compression/pruning/fine_tuner.py
"""
Post-pruning accuracy recovery fine-tuner.

After channel pruning some accuracy is lost.  This module runs a short
fine-tuning phase (typically 10–20 epochs) with a lower LR to recover it.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


@dataclass
class FineTuneConfig:
    epochs: int = 15
    lr: float = 1e-4
    grad_clip: float = 5.0


class FineTuner:
    """Recovers accuracy lost after channel pruning."""

    def __init__(self, cfg: FineTuneConfig = FineTuneConfig()):
        self.cfg = cfg

    def tune(self, model: nn.Module, datamodule,
             criterion: nn.Module) -> nn.Module:
        """
        Args:
            model:      Pruned model.
            datamodule: Provides train_dataloader().
            criterion:  MultiTaskLoss instance.

        Returns:
            Fine-tuned model.
        """
        device = next(model.parameters()).device
        optimizer = torch.optim.AdamW(model.parameters(), lr=self.cfg.lr)
        model.train()

        for epoch in range(1, self.cfg.epochs + 1):
            total_loss = 0.0
            for batch in datamodule.train_dataloader():
                images = batch['image'].to(device)
                targets = {k: v.to(device) for k, v in batch['targets'].items()}
                preds = model(images)
                loss = criterion(preds, targets)['total']
                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), self.cfg.grad_clip)
                optimizer.step()
                total_loss += loss.item()
            logger.info(f"Fine-tune epoch {epoch}/{self.cfg.epochs} "
                        f"loss={total_loss:.4f}")
        return model
