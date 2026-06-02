# features/training/trainer.py
"""
Training loop for LightFace-Net.

Responsibilities:
  - Epoch iteration with gradient accumulation support
  - Checkpoint saving (best + latest)
  - Optional TensorBoard / W&B logging
  - Mixed precision (AMP) training

All hyperparameters are supplied via TrainerConfig (from YAML).
The trainer has ZERO imports from features/data — it receives a DataModule
and calls .train_dataloader() / .val_dataloader() interfaces only.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
from torch.cuda.amp import GradScaler, autocast

from .losses import MultiTaskLoss, LossConfig
from .optimizers import build_optimizer_and_scheduler, OptimizerConfig

logger = logging.getLogger(__name__)


@dataclass
class TrainerConfig:
    epochs: int = 120
    batch_size: int = 32
    grad_clip: float = 10.0
    accum_steps: int = 1           # Gradient accumulation steps
    amp: bool = True               # Mixed precision
    checkpoint_dir: str = 'models/checkpoints'
    save_every: int = 10           # Save checkpoint every N epochs
    log_every: int = 50            # Log every N batches
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    loss: LossConfig = field(default_factory=LossConfig)
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'


class Trainer:
    """
    Orchestrates the LightFace-Net training loop.

    Example:
        trainer = Trainer(model, datamodule, TrainerConfig())
        trainer.fit()
    """

    def __init__(self, model: nn.Module, datamodule,
                 cfg: TrainerConfig = TrainerConfig()):
        self.model = model
        self.datamodule = datamodule
        self.cfg = cfg
        self.device = torch.device(cfg.device)

        self.model.to(self.device)
        self.criterion = MultiTaskLoss(cfg.loss)

        steps_per_epoch = len(datamodule.train_dataloader())
        self.optimizer, self.scheduler = build_optimizer_and_scheduler(
            model, steps_per_epoch, cfg.optimizer
        )
        self.scaler = GradScaler(enabled=cfg.amp and self.device.type == 'cuda')

        self._best_loss: float = float('inf')
        Path(cfg.checkpoint_dir).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fit(self) -> None:
        for epoch in range(1, self.cfg.epochs + 1):
            train_loss = self._train_epoch(epoch)
            val_loss = self._val_epoch(epoch)
            self.scheduler.step()

            logger.info(f"Epoch {epoch}/{self.cfg.epochs} — "
                        f"train_loss={train_loss:.4f}  val_loss={val_loss:.4f}")

            if epoch % self.cfg.save_every == 0:
                self._save_checkpoint(epoch, val_loss)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _train_epoch(self, epoch: int) -> float:
        self.model.train()
        total_loss = 0.0
        loader = self.datamodule.train_dataloader()
        self.optimizer.zero_grad()

        for step, batch in enumerate(loader, 1):
            images = batch['image'].to(self.device)
            targets = {k: v.to(self.device) for k, v in batch['targets'].items()}

            with autocast(enabled=self.cfg.amp and self.device.type == 'cuda'):
                preds = self.model(images)
                loss_dict = self.criterion(preds, targets)
                loss = loss_dict['total'] / self.cfg.accum_steps

            self.scaler.scale(loss).backward()

            if step % self.cfg.accum_steps == 0:
                self.scaler.unscale_(self.optimizer)
                nn.utils.clip_grad_norm_(self.model.parameters(),
                                         self.cfg.grad_clip)
                self.scaler.step(self.optimizer)
                self.scaler.update()
                self.optimizer.zero_grad()

            total_loss += loss_dict['total'].item()
            if step % self.cfg.log_every == 0:
                logger.info(f"  [E{epoch} S{step}] "
                            f"cls={loss_dict['cls'].item():.4f}  "
                            f"reg={loss_dict['reg'].item():.4f}")

        return total_loss / max(len(loader), 1)

    @torch.no_grad()
    def _val_epoch(self, epoch: int) -> float:
        self.model.eval()
        total_loss = 0.0
        loader = self.datamodule.val_dataloader()
        for batch in loader:
            images = batch['image'].to(self.device)
            targets = {k: v.to(self.device) for k, v in batch['targets'].items()}
            preds = self.model(images)
            loss_dict = self.criterion(preds, targets)
            total_loss += loss_dict['total'].item()
        return total_loss / max(len(loader), 1)

    def _save_checkpoint(self, epoch: int, val_loss: float) -> None:
        ckpt = {
            'epoch': epoch,
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'val_loss': val_loss,
        }
        path = Path(self.cfg.checkpoint_dir) / f'epoch_{epoch:04d}.pth'
        torch.save(ckpt, path)
        logger.info(f"  Saved checkpoint → {path}")

        if val_loss < self._best_loss:
            self._best_loss = val_loss
            best_path = Path(self.cfg.checkpoint_dir) / 'best.pth'
            torch.save(ckpt, best_path)
            logger.info(f"  New best model saved → {best_path}")
