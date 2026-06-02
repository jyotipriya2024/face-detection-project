# apps/demo/components/__init__.py
"""UI widget components for the Streamlit demo."""
from .fps_counter import FPSCounter
from .heatmap_viewer import render_heatmap_panel

__all__ = ["FPSCounter", "render_heatmap_panel"]
