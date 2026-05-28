# features/evaluation/benchmarks/hardware_eval.py
"""
Hardware-specific benchmark: measures FPS and memory on Jetson Nano / RPi 4B.

Run this script ON the target device after deploying the model.
Results are compared against Table 5.2 in the thesis.
"""

from __future__ import annotations
import json
import logging
import platform
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from features.evaluation.metrics import FPSProfiler, ProfilerConfig, profile_memory

logger = logging.getLogger(__name__)


@dataclass
class HardwareBenchmarkConfig:
    input_sizes: list = None
    output_json: str = 'hardware_benchmark_results.json'
    warmup_runs: int = 20
    benchmark_runs: int = 200

    def __post_init__(self):
        if self.input_sizes is None:
            self.input_sizes = [(640, 480), (320, 240), (1280, 720)]


def run_hardware_benchmark(pipeline, cfg: HardwareBenchmarkConfig = None) -> dict:
    """
    Benchmark LightFace-Net at multiple input resolutions on the current device.

    Args:
        pipeline: DetectionPipeline in eval mode.
        cfg:      HardwareBenchmarkConfig.

    Returns:
        Dictionary of benchmark results keyed by resolution.
    """
    if cfg is None:
        cfg = HardwareBenchmarkConfig()

    profiler = FPSProfiler(ProfilerConfig(
        warmup_runs=cfg.warmup_runs,
        benchmark_runs=cfg.benchmark_runs,
    ))

    results = {
        'device': platform.node(),
        'platform': platform.machine(),
        'torch_version': torch.__version__,
        'resolutions': {},
    }

    for w, h in cfg.input_sizes:
        dummy = np.zeros((h, w, 3), dtype=np.uint8)
        fps_result = profiler.profile(pipeline.detect, dummy)
        mem_report = profile_memory(pipeline.detect, pipeline, dummy)

        key = f'{w}x{h}'
        results['resolutions'][key] = {
            'fps': round(fps_result.fps, 2),
            'latency_mean_ms': round(fps_result.latency_mean_ms, 2),
            'latency_p95_ms': round(fps_result.latency_p95_ms, 2),
            'peak_vram_mb': round(mem_report.peak_vram_mb, 2),
            'model_size_mb': round(mem_report.model_size_mb, 2),
        }
        logger.info(f"  {key}: {fps_result}")

    out_path = Path(cfg.output_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Hardware benchmark saved → {out_path}")
    return results
