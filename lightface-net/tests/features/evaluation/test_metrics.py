# tests/features/evaluation/test_metrics.py
"""
Unit tests for AP computation and FPS profiler.

Run:
    pytest tests/features/evaluation/ -v
"""

import pytest
import numpy as np


class TestComputeAP:
    def test_perfect_detector_ap_is_1(self):
        from features.evaluation.metrics.average_precision import compute_ap
        recall    = np.linspace(0, 1, 11)
        precision = np.ones(11)
        ap = compute_ap(precision, recall)
        assert ap == pytest.approx(1.0, abs=1e-3)

    def test_random_recall_precision_returns_float(self):
        from features.evaluation.metrics.average_precision import compute_ap
        recall    = np.array([0.0, 0.2, 0.5, 0.8, 1.0])
        precision = np.array([1.0, 0.9, 0.7, 0.5, 0.3])
        ap = compute_ap(precision, recall)
        assert 0.0 <= ap <= 1.0

    def test_zero_precision_recall_ap_is_0(self):
        from features.evaluation.metrics.average_precision import compute_ap
        recall    = np.zeros(5)
        precision = np.zeros(5)
        ap = compute_ap(precision, recall)
        assert ap == pytest.approx(0.0, abs=1e-3)


class TestComputeIoU:
    def test_perfect_overlap(self):
        from features.evaluation.metrics.average_precision import compute_iou
        box = np.array([0, 0, 10, 10], dtype=float)
        iou = compute_iou(box, box)
        assert iou == pytest.approx(1.0)

    def test_no_overlap(self):
        from features.evaluation.metrics.average_precision import compute_iou
        b1 = np.array([0, 0, 5, 5], dtype=float)
        b2 = np.array([10, 10, 20, 20], dtype=float)
        assert compute_iou(b1, b2) == pytest.approx(0.0)

    def test_half_overlap(self):
        from features.evaluation.metrics.average_precision import compute_iou
        b1 = np.array([0, 0, 4, 4], dtype=float)
        b2 = np.array([2, 0, 6, 4], dtype=float)
        iou = compute_iou(b1, b2)
        assert 0.0 < iou < 1.0


class TestFPSProfiler:
    def test_returns_profiler_result(self):
        from features.evaluation.metrics.fps_profiler import FPSProfiler, ProfilerConfig
        import torch

        model = torch.nn.Linear(16, 8)
        dummy = torch.randn(1, 16)
        profiler = FPSProfiler(ProfilerConfig(warmup_runs=2, benchmark_runs=5))
        result = profiler.profile(model, dummy)
        assert result.fps > 0
        assert result.latency_mean_ms > 0
