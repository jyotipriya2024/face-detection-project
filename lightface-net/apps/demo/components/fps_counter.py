# apps/demo/components/fps_counter.py
"""Rolling FPS counter widget for the Streamlit demo."""

from __future__ import annotations
from collections import deque
import time


class FPSCounter:
    """
    Maintains a rolling window of frame timestamps to compute smoothed FPS.

    Args:
        window: Number of recent frames to average over.
    """

    def __init__(self, window: int = 30):
        self._timestamps: deque[float] = deque(maxlen=window)

    def tick(self) -> float:
        """Record a new frame timestamp and return current FPS."""
        self._timestamps.append(time.perf_counter())
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        return (len(self._timestamps) - 1) / max(elapsed, 1e-6)

    @property
    def fps(self) -> float:
        """Most recent smoothed FPS value."""
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        return (len(self._timestamps) - 1) / max(elapsed, 1e-6)
