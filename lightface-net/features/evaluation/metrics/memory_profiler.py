# features/evaluation/metrics/memory_profiler.py
"""
GPU VRAM and system RAM footprint profiler.

Reports peak memory allocation during a single inference pass.
Used to validate the <10 MB INT8 model footprint requirement.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

import torch
import os


@dataclass
class MemoryReport:
    peak_vram_mb: float     # Peak GPU VRAM allocated during inference
    model_size_mb: float    # Model parameter footprint
    ram_mb: float           # Approximate resident set size (RSS)

    def __str__(self) -> str:
        return (
            f"Model size: {self.model_size_mb:.2f} MB  |  "
            f"Peak VRAM: {self.peak_vram_mb:.2f} MB  |  "
            f"RAM RSS: {self.ram_mb:.1f} MB"
        )


def model_size_mb(model: torch.nn.Module) -> float:
    """Returns model parameter size in MB (FP32 bytes / 1M)."""
    total_bytes = sum(
        p.numel() * p.element_size() for p in model.parameters()
    )
    return total_bytes / (1024 ** 2)


def profile_memory(fn: Callable, model: torch.nn.Module,
                   *args, **kwargs) -> MemoryReport:
    """
    Profile peak VRAM during inference.

    Args:
        fn:    The inference callable (e.g. pipeline.detect).
        model: The model whose parameters are being measured.
        *args: Positional arguments forwarded to fn.

    Returns:
        MemoryReport
    """
    # GPU peak
    peak_vram = 0.0
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        fn(*args, **kwargs)
        peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 2)

    # RSS (Linux/macOS via /proc, Windows via psutil)
    rss_mb = 0.0
    try:
        import psutil
        process = psutil.Process(os.getpid())
        rss_mb = process.memory_info().rss / (1024 ** 2)
    except ImportError:
        pass

    return MemoryReport(
        peak_vram_mb=peak_vram,
        model_size_mb=model_size_mb(model),
        ram_mb=rss_mb,
    )
