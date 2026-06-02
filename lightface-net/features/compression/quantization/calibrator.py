# features/compression/quantization/calibrator.py
"""
KL-divergence calibration for INT8 post-training quantization.

Calibration determines optimal dynamic ranges for activation tensors by
minimizing the KL-divergence between FP32 and INT8 distributions across
a representative calibration dataset (~1000 images from WIDER FACE).
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


@dataclass
class CalibrationConfig:
    num_calibration_images: int = 1024
    histogram_bins: int = 2048
    percentile: float = 99.99      # Clip outliers beyond this percentile


class KLCalibrator:
    """
    Runs calibration forward passes to collect activation histograms,
    then solves for per-tensor INT8 scales using KL-divergence minimization.

    This is the same algorithm used by NVIDIA TensorRT's MinMax calibrator.
    """

    def __init__(self, cfg: CalibrationConfig = CalibrationConfig()):
        self.cfg = cfg
        self._hooks: list = []
        self._histograms: Dict[str, np.ndarray] = {}

    def _register_hooks(self, model: nn.Module) -> None:
        """Attach forward hooks to capture activation distributions."""
        def make_hook(name: str):
            def hook(module, inp, out):
                vals = out.detach().cpu().float().numpy().flatten()
                counts, _ = np.histogram(
                    np.abs(vals),
                    bins=self.cfg.histogram_bins,
                    range=(0, np.abs(vals).max() + 1e-8),
                )
                if name not in self._histograms:
                    self._histograms[name] = counts
                else:
                    self._histograms[name] += counts
            return hook

        for name, module in model.named_modules():
            if isinstance(module, (nn.Conv2d, nn.Linear)):
                h = module.register_forward_hook(make_hook(name))
                self._hooks.append(h)

    def _remove_hooks(self) -> None:
        for h in self._hooks:
            h.remove()
        self._hooks.clear()

    @staticmethod
    def _kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
        p = p.astype(np.float64) + 1e-12
        q = q.astype(np.float64) + 1e-12
        p /= p.sum()
        q /= q.sum()
        return float(np.sum(p * np.log(p / q)))

    def calibrate(self, model: nn.Module,
                  dataloader) -> Dict[str, float]:
        """
        Run calibration and return per-layer INT8 scale factors.

        Args:
            model:      FP32 model in eval mode.
            dataloader: Calibration data (images only).

        Returns:
            {layer_name: scale_factor}
        """
        model.eval()
        self._register_hooks(model)

        collected = 0
        with torch.no_grad():
            for batch in dataloader:
                if collected >= self.cfg.num_calibration_images:
                    break
                images = batch['image'] if isinstance(batch, dict) else batch
                model(images)
                collected += images.shape[0]

        self._remove_hooks()

        scales: Dict[str, float] = {}
        for name, hist in self._histograms.items():
            # Find threshold that minimises KL(FP32_distribution || INT8_distribution)
            best_threshold_idx = self._histogram_bins - 1
            best_kl = float('inf')
            for i in range(128, len(hist)):
                # Reference distribution: first i bins
                ref = hist[:i].copy()
                ref[-1] += hist[i:].sum()
                # Quantized distribution: re-bin to 128 levels (INT8)
                quant = np.zeros(128)
                bins_per_level = i / 128.0
                for j in range(128):
                    lo = int(j * bins_per_level)
                    hi = int((j + 1) * bins_per_level)
                    quant[j] = ref[lo:hi].sum()
                # Upsample back for comparison
                expanded = np.repeat(quant / (bins_per_level or 1), int(np.ceil(bins_per_level)))[:i]
                kl = self._kl_divergence(ref[:i], expanded[:i])
                if kl < best_kl:
                    best_kl = kl
                    best_threshold_idx = i
            # Scale = threshold / 127
            max_range = hist.shape[0]
            scale = (best_threshold_idx / max_range) / 127.0
            scales[name] = scale
            logger.debug(f"  {name}: scale={scale:.6f}")

        logger.info(f"Calibration complete — {len(scales)} layers calibrated")
        return scales
