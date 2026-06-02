# features/compression/pruning/sparsity_trainer.py
"""
L1 sparsity regularisation on BatchNorm gamma coefficients.

Before pruning, the model is fine-tuned with an additional penalty
  L_sparse = lambda_sparse * sum(|gamma_i|)
added to the task loss.  This drives unimportant channel scaling
factors toward zero, making them safe to remove without accuracy loss.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


@dataclass
class SparsityConfig:
    lambda_sparse: float = 1e-4    # L1 penalty weight
    epochs: int = 30               # Additional sparsity training epochs
    lr: float = 1e-4


class SparsityTrainer:
    """
    Adds BN-gamma L1 penalty to the loss and runs a short sparsity-inducing
    training phase.  Returns the sparsified model (weights unchanged in shape).
    """

    def __init__(self, cfg: SparsityConfig = SparsityConfig()):
        self.cfg = cfg

    def _gamma_l1_penalty(self, model: nn.Module) -> torch.Tensor:
        """Sum of absolute BN gamma values across the entire model."""
        penalty = torch.tensor(0.0)
        for m in model.modules():
            if isinstance(m, nn.BatchNorm2d):
                penalty = penalty + m.weight.abs().sum()
        return penalty

    def train(self, model: nn.Module, datamodule,
              base_criterion: nn.Module) -> nn.Module:
        """
        Run sparsity-inducing training.

        Args:
            model:          The LightFace-Net model to sparsify.
            datamodule:     Provides train_dataloader().
            base_criterion: The MultiTaskLoss instance.

        Returns:
            The same model with BN gammas driven toward sparsity.
        """
        device = next(model.parameters()).device
        optimizer = torch.optim.AdamW(model.parameters(), lr=self.cfg.lr)
        model.train()

        for epoch in range(1, self.cfg.epochs + 1):
            epoch_loss = 0.0
            for batch in datamodule.train_dataloader():
                images = batch['image'].to(device)
                targets = {k: v.to(device) for k, v in batch['targets'].items()}

                preds = model(images)
                task_loss = base_criterion(preds, targets)['total']
                sparse_loss = self._gamma_l1_penalty(model) * self.cfg.lambda_sparse
                total = task_loss + sparse_loss

                optimizer.zero_grad()
                total.backward()
                optimizer.step()
                epoch_loss += total.item()

            logger.info(f"Sparsity epoch {epoch}/{self.cfg.epochs} "
                        f"loss={epoch_loss:.4f}")
        return model
