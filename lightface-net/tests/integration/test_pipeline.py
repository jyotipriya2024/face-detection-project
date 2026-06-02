# tests/integration/test_pipeline.py
"""
End-to-end integration test: dummy frame → DetectionPipeline.detect().

Run:
    pytest tests/integration/ -v
"""

import numpy as np
import pytest


class TestDetectionPipelineIntegration:
    @pytest.fixture(scope='class')
    def pipeline(self):
        from features.detection.pipeline import DetectionPipeline
        return DetectionPipeline()

    def test_detect_returns_list(self, pipeline):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = pipeline.detect(frame)
        assert isinstance(detections, list)

    def test_bounding_box_fields(self, pipeline):
        """Each detection must have x1,y1,x2,y2,score attributes."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        detections = pipeline.detect(frame)
        for d in detections:
            assert hasattr(d, 'x1')
            assert hasattr(d, 'y1')
            assert hasattr(d, 'x2')
            assert hasattr(d, 'y2')
            assert hasattr(d, 'score')
            assert 0.0 <= d.score <= 1.0

    def test_bounding_box_ordering(self, pipeline):
        """x2 > x1 and y2 > y1 for all detections."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        for d in pipeline.detect(frame):
            assert d.x2 > d.x1
            assert d.y2 > d.y1

    def test_performance_metrics_populated(self, pipeline):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        pipeline.detect(frame)
        metrics = pipeline.get_performance_metrics()
        assert 'fps' in metrics
        assert 'latency_ms' in metrics
