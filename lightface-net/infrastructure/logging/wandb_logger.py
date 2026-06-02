# infrastructure/logging/wandb_logger.py
"""
Weights & Biases experiment tracking logger.

Tracks training curves, model checkpoints, ablation tables, and system metrics.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

try:
    import wandb
    _WANDB_AVAILABLE = True
except ImportError:
    _WANDB_AVAILABLE = False
    logger.warning("W&B not installed. `pip install wandb`")


class WandBLogger:
    """
    Logs metrics and artifacts to Weights & Biases.

    Usage:
        wb = WandBLogger(project='lightface-net', name='exp_afpn_v1')
        wb.log({'train/loss': 0.5, 'val/AP': 0.82})
        wb.finish()
    """

    def __init__(self, project: str = 'lightface-net',
                 name: Optional[str] = None,
                 config: Optional[Dict] = None,
                 offline: bool = False):
        self._run = None
        if _WANDB_AVAILABLE:
            mode = 'offline' if offline else 'online'
            self._run = wandb.init(
                project=project, name=name, config=config, mode=mode,
                reinit=True,
            )
            logger.info(f"W&B run: {self._run.url if hasattr(self._run, 'url') else 'offline'}")
        else:
            logger.warning("W&B unavailable — experiment tracking disabled.")

    def log(self, metrics: Dict[str, Any], step: Optional[int] = None) -> None:
        if self._run is None:
            return
        wandb.log(metrics, step=step)

    def log_artifact(self, path: str, artifact_type: str = 'model',
                     name: Optional[str] = None) -> None:
        if self._run is None:
            return
        artifact = wandb.Artifact(name or path, type=artifact_type)
        artifact.add_file(path)
        wandb.log_artifact(artifact)

    def finish(self) -> None:
        if self._run:
            wandb.finish()
