# features/evaluation/metrics/fps_profiler.py
"""
FPS and latency profiler.

Measures end-to-end inference latency using CUDA events (when available)
or wall-clock time, averaged over a warm-up + benchmark run.
"""

from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Callable

import torch


@dataclass
class ProfilerConfig:
    warmup_runs: int = 10
    benchmark_runs: int = 100


@dataclass
class ProfilerResult:
    fps: float
    latency_mean_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float

    def __str__(self) -> str:
        return (
            f"FPS: {self.fps:.1f}  |  "
            f"Latency (mean/p50/p95/p99): "
            f"{self.latency_mean_ms:.1f} / "
            f"{self.latency_p50_ms:.1f} / "
            f"{self.latency_p95_ms:.1f} / "
            f"{self.latency_p99_ms:.1f} ms"
        )


class FPSProfiler:
    """
    Profiles a callable (model forward or full detect() pipeline).

    Example:
        profiler = FPSProfiler()
        result = profiler.profile(pipeline.detect, dummy_image)
        print(result)
    """

    def __init__(self, cfg: ProfilerConfig = ProfilerConfig()):
        self.cfg = cfg

    def profile(self, fn: Callable, *args, **kwargs) -> ProfilerResult:
        use_cuda = torch.cuda.is_available()
        if use_cuda:
            torch.cuda.synchronize()

        # Warm-up
        for _ in range(self.cfg.warmup_runs):
            fn(*args, **kwargs)

        # Benchmark
        latencies = []
        for _ in range(self.cfg.benchmark_runs):
            if use_cuda:
                start = torch.cuda.Event(enable_timing=True)
                end = torch.cuda.Event(enable_timing=True)
                start.record()
                fn(*args, **kwargs)
                end.record()
                torch.cuda.synchronize()
                latencies.append(start.elapsed_time(end))
            else:
                t0 = time.perf_counter()
                fn(*args, **kwargs)
                latencies.append((time.perf_counter() - t0) * 1000.0)

        import numpy as np
        arr = sorted(latencies)
        mean_ms = float(sum(arr) / len(arr))
        return ProfilerResult(
            fps=1000.0 / max(mean_ms, 1e-3),
            latency_mean_ms=mean_ms,
            latency_p50_ms=float(arr[int(0.50 * len(arr))]),
            latency_p95_ms=float(arr[int(0.95 * len(arr))]),
            latency_p99_ms=float(arr[int(0.99 * len(arr))]),
        )
