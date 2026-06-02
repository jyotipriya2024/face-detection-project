# features/compression/quantization/int8_quantizer.py
"""
Post-training INT8 quantization for LightFace-Net.

On non-Jetson platforms this module uses PyTorch's native static
quantization (torch.quantization) as the fallback path.
On Jetson Nano (JetPack 4.6+), quantization is performed via TensorRT
through the tensorrt_export module.
"""

from __future__ import annotations
import copy
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import torch
import torch.nn as nn

from .calibrator import KLCalibrator, CalibrationConfig

logger = logging.getLogger(__name__)


@dataclass
class QuantConfig:
    backend: str = 'pytorch'       # 'pytorch' | 'tensorrt'
    output_dir: str = 'models/quantized'
    calibration: CalibrationConfig = None

    def __post_init__(self):
        if self.calibration is None:
            self.calibration = CalibrationConfig()


class INT8Quantizer:
    """
    Applies post-training INT8 quantization via PyTorch static quantization.

    For TensorRT export on Jetson Nano, use tensorrt_export.TensorRTExporter.
    """

    def __init__(self, cfg: QuantConfig = QuantConfig()):
        self.cfg = cfg
        self.calibrator = KLCalibrator(cfg.calibration)

    def export(self, model: nn.Module,
               calibration_dataloader,
               output_path: str | None = None) -> nn.Module:
        """
        Quantize and save the model.

        Args:
            model:                   Fine-tuned FP32 model.
            calibration_dataloader:  DataLoader for calibration (no grad needed).
            output_path:             Where to save the quantized .pth.

        Returns:
            INT8 quantized model.
        """
        if self.cfg.backend == 'tensorrt':
            logger.warning(
                "TensorRT backend requested — call "
                "quantization.tensorrt_export.TensorRTExporter instead."
            )
            return model

        # --- PyTorch static quantization path ---
        model_to_quant = copy.deepcopy(model).cpu().eval()
        model_to_quant.qconfig = torch.quantization.get_default_qconfig('fbgemm')
        torch.quantization.prepare(model_to_quant, inplace=True)

        # Calibration forward passes
        logger.info("Running calibration forward passes …")
        collected = 0
        with torch.no_grad():
            for batch in calibration_dataloader:
                if collected >= self.cfg.calibration.num_calibration_images:
                    break
                images = batch['image'] if isinstance(batch, dict) else batch
                model_to_quant(images.cpu())
                collected += images.shape[0]
                logger.info(f"  Calibrated {collected} images")

        torch.quantization.convert(model_to_quant, inplace=True)
        logger.info("INT8 quantization complete.")

        # Save
        out_dir = Path(self.cfg.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        save_path = output_path or str(out_dir / 'lightfacenet_int8.pth')
        torch.save(model_to_quant.state_dict(), save_path)
        logger.info(f"Saved INT8 model → {save_path}")

        return model_to_quant
