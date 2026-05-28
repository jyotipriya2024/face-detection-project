# infrastructure/logging/tensorboard_logger.py
"""
TensorBoard training metrics logger.

Wraps torch.utils.tensorboard.SummaryWriter to provide
a consistent logging interface for the Trainer.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

try:
    from torch.utils.tensorboard import SummaryWriter
    _TB_AVAILABLE = True
except ImportError:
    _TB_AVAILABLE = False
    logger.warning("TensorBoard not installed. `pip install tensorboard`")


class TensorBoardLogger:
    """
    Logs scalar metrics, images, and histograms to TensorBoard.

    Usage:
        tb = TensorBoardLogger('runs/exp_001')
        tb.log_scalars({'train/loss': 0.5, 'val/AP': 0.82}, step=100)
    """

    def __init__(self, log_dir: str = 'runs'):
        self._writer: Optional[object] = None
        if _TB_AVAILABLE:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            self._writer = SummaryWriter(log_dir=log_dir)
            logger.info(f"TensorBoard logging → {log_dir}")
        else:
            logger.warning("TensorBoard unavailable — logging disabled.")

    def log_scalars(self, metrics: Dict[str, float], step: int) -> None:
        if self._writer is None:
            return
        for tag, value in metrics.items():
            self._writer.add_scalar(tag, value, global_step=step)

    def log_histogram(self, tag: str, values, step: int) -> None:
        if self._writer is None:
            return
        self._writer.add_histogram(tag, values, global_step=step)

    def log_image(self, tag: str, image, step: int) -> None:
        if self._writer is None:
            return
        self._writer.add_image(tag, image, global_step=step)

    def close(self) -> None:
        if self._writer:
            self._writer.close()
