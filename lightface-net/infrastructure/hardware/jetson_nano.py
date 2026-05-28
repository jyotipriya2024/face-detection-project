# infrastructure/hardware/jetson_nano.py
"""
Jetson Nano-specific optimizations and helpers.

Handles:
- Power mode switching (nvpmodel)
- Jetson clocks maximisation
- TensorRT engine loading and inference
- GPIO / camera CSI interface helpers
"""

from __future__ import annotations
import logging
import subprocess
import os
from pathlib import Path
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)


def set_max_performance() -> bool:
    """
    Set Jetson Nano to MAXN power mode (all cores at max clock).
    Requires root / sudo access on device.

    Returns:
        True if successful.
    """
    try:
        subprocess.run(['sudo', 'nvpmodel', '-m', '0'], check=True,
                       capture_output=True)
        subprocess.run(['sudo', 'jetson_clocks'], check=True,
                       capture_output=True)
        logger.info("Jetson Nano set to MAXN performance mode.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("nvpmodel/jetson_clocks not available — "
                       "not running on Jetson Nano.")
        return False


def get_jetson_stats() -> dict:
    """
    Read Jetson tegrastats output for current power/thermal stats.
    Returns empty dict if not on Jetson.
    """
    try:
        result = subprocess.run(
            ['tegrastats', '--interval', '1', '--stop'],
            capture_output=True, text=True, timeout=3
        )
        line = result.stdout.strip().split('\n')[-1] if result.stdout else ''
        return {'raw_tegrastats': line}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {}


class TRTInferenceEngine:
    """
    Wraps a serialized TensorRT INT8 engine for Jetson Nano inference.

    Usage:
        engine = TRTInferenceEngine('models/quantized/lightfacenet_int8.trt')
        output = engine.infer(frame_bgr)
    """

    def __init__(self, engine_path: str):
        self._engine_path = engine_path
        self._context = None
        self._load_engine()

    def _load_engine(self) -> None:
        try:
            import tensorrt as trt
            import pycuda.driver as cuda
            import pycuda.autoinit  # noqa: F401

            TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
            with open(self._engine_path, 'rb') as f, \
                 trt.Runtime(TRT_LOGGER) as runtime:
                engine = runtime.deserialize_cuda_engine(f.read())
            self._context = engine.create_execution_context()
            logger.info(f"TRT engine loaded: {self._engine_path}")
        except ImportError:
            logger.warning("TensorRT / PyCUDA not available on this platform.")

    def is_available(self) -> bool:
        return self._context is not None

    def infer(self, frame_bgr: np.ndarray) -> Optional[list]:
        """Run inference.  Returns raw output buffers or None if unavailable."""
        if not self.is_available():
            return None
        # (Actual TRT binding / buffer management omitted — device-specific)
        raise NotImplementedError(
            "Run this on Jetson Nano with TensorRT + PyCUDA installed."
        )
