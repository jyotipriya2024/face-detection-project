# infrastructure/hardware/raspberry_pi.py
"""
Raspberry Pi 4B deployment helpers.

Uses ONNX Runtime (with ARM optimizations) as the inference backend on Pi.
TensorRT is not available on Pi; FP32 / FP16 via ONNX Runtime is used instead.

Target performance: ~8 FPS at 320×240 input.
"""

from __future__ import annotations
import logging
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import onnxruntime as ort
    _ORT_AVAILABLE = True
except ImportError:
    _ORT_AVAILABLE = False
    logger.warning("ONNX Runtime not installed. `pip install onnxruntime`")


class OnnxInferenceEngine:
    """
    ONNX Runtime inference engine for Raspberry Pi 4B.

    Usage:
        engine = OnnxInferenceEngine('models/quantized/lightfacenet.onnx')
        outputs = engine.infer(preprocessed_tensor)
    """

    def __init__(self, onnx_path: str, num_threads: int = 4):
        self._session: Optional[object] = None
        if _ORT_AVAILABLE:
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = num_threads
            opts.inter_op_num_threads = 1
            opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            self._session = ort.InferenceSession(
                onnx_path, sess_options=opts,
                providers=['CPUExecutionProvider']
            )
            logger.info(f"ONNX Runtime session loaded: {onnx_path}")
        else:
            logger.warning("ONNX Runtime unavailable — install onnxruntime.")

    def is_available(self) -> bool:
        return self._session is not None

    def infer(self, input_array: np.ndarray) -> Optional[List[np.ndarray]]:
        """
        Run inference on a pre-processed input tensor.

        Args:
            input_array: (1, 3, H, W) float32 normalised numpy array.

        Returns:
            List of output arrays, or None if unavailable.
        """
        if not self.is_available():
            return None
        input_name = self._session.get_inputs()[0].name
        return self._session.run(None, {input_name: input_array})
