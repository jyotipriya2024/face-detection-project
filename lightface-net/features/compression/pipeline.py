# features/compression/pipeline.py
"""
Full model compression orchestrator.

Pipeline stages (in order):
  1. Sparsity training  — L1 penalty on BN gamma drives channels toward zero
  2. Channel pruning    — Remove channels with |gamma| < global threshold
  3. Fine-tuning        — Recover accuracy lost after pruning
  4. INT8 quantization  — Post-training quantization via PyTorch / TensorRT

Each stage is independently configurable and the pipeline returns a
CompressionResult with both the compressed model and profiling metrics.
"""

from __future__ import annotations
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import torch
import torch.nn as nn

from .pruning import SparsityTrainer, SparsityConfig, BNPruner, PrunerConfig, FineTuner, FineTuneConfig
from .quantization import INT8Quantizer, QuantConfig, TensorRTExporter, TRTExportConfig
from features.training.losses import MultiTaskLoss, LossConfig

logger = logging.getLogger(__name__)


@dataclass
class CompressionResult:
    model: nn.Module
    engine_path: Optional[str]
    fp32_size_mb: float
    int8_size_mb: float
    param_reduction_pct: float
    total_time_sec: float


@dataclass
class CompressionPipelineConfig:
    sparsity: SparsityConfig = field(default_factory=SparsityConfig)
    pruner: PrunerConfig = field(default_factory=PrunerConfig)
    fine_tune: FineTuneConfig = field(default_factory=FineTuneConfig)
    quant: QuantConfig = field(default_factory=QuantConfig)
    trt: TRTExportConfig = field(default_factory=TRTExportConfig)
    loss: LossConfig = field(default_factory=LossConfig)
    skip_sparsity: bool = False
    skip_pruning: bool = False
    skip_quantization: bool = False
    use_tensorrt: bool = False


def _count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


def _model_size_mb(model: nn.Module) -> float:
    total = sum(p.numel() * p.element_size() for p in model.parameters())
    return total / (1024 ** 2)


class CompressionPipeline:
    """
    Orchestrates: Train → Sparse Train → Prune → Fine-tune → INT8 Export

    Example:
        pipeline = CompressionPipeline(CompressionPipelineConfig())
        result = pipeline.run(model, datamodule)
        print(f"INT8 size: {result.int8_size_mb:.1f} MB")
    """

    def __init__(self, cfg: CompressionPipelineConfig = CompressionPipelineConfig()):
        self.cfg = cfg
        self.criterion = MultiTaskLoss(cfg.loss)
        self.sparsity_trainer = SparsityTrainer(cfg.sparsity)
        self.bn_pruner = BNPruner(cfg.pruner)
        self.fine_tuner = FineTuner(cfg.fine_tune)
        self.int8_quantizer = INT8Quantizer(cfg.quant)
        self.trt_exporter = TensorRTExporter(cfg.trt) if cfg.use_tensorrt else None

    def run(self, model: nn.Module,
            datamodule) -> CompressionResult:
        t0 = time.perf_counter()
        fp32_size = _model_size_mb(model)
        fp32_params = _count_params(model)

        # --- Stage 1: Sparsity training ---
        if not self.cfg.skip_sparsity:
            logger.info("Stage 1/4 — Sparsity training")
            model = self.sparsity_trainer.train(model, datamodule, self.criterion)

        # --- Stage 2: Channel pruning ---
        if not self.cfg.skip_pruning:
            logger.info("Stage 2/4 — Channel pruning")
            model = self.bn_pruner.prune(model)

        # --- Stage 3: Fine-tuning ---
        if not self.cfg.skip_pruning:
            logger.info("Stage 3/4 — Post-prune fine-tuning")
            model = self.fine_tuner.tune(model, datamodule, self.criterion)

        # --- Stage 4: INT8 quantization ---
        engine_path = None
        if not self.cfg.skip_quantization:
            logger.info("Stage 4/4 — INT8 quantization")
            if self.cfg.use_tensorrt and self.trt_exporter:
                engine_path = self.trt_exporter.export(
                    model, datamodule.calibration_dataloader()
                )
            else:
                model = self.int8_quantizer.export(
                    model, datamodule.calibration_dataloader()
                )

        pruned_params = _count_params(model)
        int8_size = _model_size_mb(model)
        param_reduction_pct = 100 * (1 - pruned_params / max(fp32_params, 1))
        total_time = time.perf_counter() - t0

        logger.info(
            f"Compression complete — "
            f"FP32: {fp32_size:.1f}MB → INT8: {int8_size:.1f}MB  "
            f"Params reduced by {param_reduction_pct:.1f}%  "
            f"Time: {total_time:.0f}s"
        )
        return CompressionResult(
            model=model,
            engine_path=engine_path,
            fp32_size_mb=fp32_size,
            int8_size_mb=int8_size,
            param_reduction_pct=param_reduction_pct,
            total_time_sec=total_time,
        )
