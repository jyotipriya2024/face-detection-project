# features/compression/quantization/tensorrt_export.py
"""
TensorRT INT8 engine builder for NVIDIA Jetson Nano deployment.

Pipeline:
  PyTorch model → ONNX (opset 17) → TensorRT INT8 engine (.trt)

Requirements (Jetson / x86 with TensorRT):
  pip install nvidia-tensorrt  (or use the JetPack-bundled version)

On systems without TensorRT this module gracefully degrades and logs
a warning, so the rest of the codebase continues to function.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


@dataclass
class TRTExportConfig:
    onnx_path: str = 'models/quantized/lightfacenet.onnx'
    engine_path: str = 'models/quantized/lightfacenet_int8.trt'
    input_shape: tuple = (1, 3, 480, 640)   # (N, C, H, W)
    workspace_gb: int = 4
    fp16_fallback: bool = True              # Use FP16 for unsupported INT8 ops


class TensorRTExporter:
    """
    Exports LightFace-Net to a TensorRT INT8 engine.

    Usage:
        exporter = TensorRTExporter(TRTExportConfig())
        exporter.export(model, calibration_dataloader)
    """

    def __init__(self, cfg: TRTExportConfig = TRTExportConfig()):
        self.cfg = cfg
        self._trt_available = self._check_trt()

    @staticmethod
    def _check_trt() -> bool:
        try:
            import tensorrt as trt  # noqa: F401
            return True
        except ImportError:
            logger.warning(
                "TensorRT not found.  Install nvidia-tensorrt or run on "
                "Jetson Nano with JetPack 4.6+.  Skipping TRT export."
            )
            return False

    def _export_onnx(self, model: nn.Module) -> str:
        """Export PyTorch model to ONNX opset 17."""
        import torch.onnx
        model.eval().cpu()
        dummy = torch.randn(*self.cfg.input_shape)
        Path(self.cfg.onnx_path).parent.mkdir(parents=True, exist_ok=True)
        torch.onnx.export(
            model, dummy, self.cfg.onnx_path,
            opset_version=17,
            input_names=['input'],
            output_names=['cls_F3', 'reg_F3', 'cls_F4', 'reg_F4', 'cls_F5', 'reg_F5'],
            dynamic_axes={'input': {0: 'batch'}},
        )
        logger.info(f"ONNX exported → {self.cfg.onnx_path}")
        return self.cfg.onnx_path

    def _build_engine(self, onnx_path: str,
                      calibration_dataloader) -> str:
        """Build TensorRT INT8 engine from ONNX graph."""
        import tensorrt as trt

        TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
        with trt.Builder(TRT_LOGGER) as builder, \
             builder.create_network(
                 1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
             ) as network, \
             trt.OnnxParser(network, TRT_LOGGER) as parser, \
             builder.create_builder_config() as config:

            config.max_workspace_size = self.cfg.workspace_gb * (1 << 30)
            config.set_flag(trt.BuilderFlag.INT8)
            if self.cfg.fp16_fallback:
                config.set_flag(trt.BuilderFlag.FP16)

            with open(onnx_path, 'rb') as f:
                if not parser.parse(f.read()):
                    for i in range(parser.num_errors):
                        logger.error(parser.get_error(i))
                    raise RuntimeError("ONNX parsing failed.")

            engine = builder.build_engine(network, config)
            if engine is None:
                raise RuntimeError("TensorRT engine build failed.")

            Path(self.cfg.engine_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.cfg.engine_path, 'wb') as f:
                f.write(engine.serialize())
            logger.info(f"TRT engine saved → {self.cfg.engine_path}")
        return self.cfg.engine_path

    def export(self, model: nn.Module,
               calibration_dataloader) -> str | None:
        """
        Full export pipeline: PyTorch → ONNX → TRT INT8 engine.

        Returns:
            Path to .trt engine file, or None if TRT unavailable.
        """
        if not self._trt_available:
            return None
        onnx_path = self._export_onnx(model)
        engine_path = self._build_engine(onnx_path, calibration_dataloader)
        return engine_path
