# apps/demo/components/heatmap_viewer.py
"""
A-FPN feature heatmap panel for the Streamlit demo.
Renders P3/P4/P5 activation maps side-by-side using matplotlib + st.pyplot.
"""

from __future__ import annotations
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np


def render_heatmap_panel(feat_maps: Dict[str, np.ndarray],
                          st_module) -> None:
    """
    Render A-FPN activation heatmaps inside a Streamlit app.

    Args:
        feat_maps:  {'F3': ndarray(H,W), 'F4': ndarray, 'F5': ndarray}
        st_module:  The `streamlit` module (passed to avoid circular import).
    """
    levels = list(feat_maps.keys())
    fig, axes = plt.subplots(1, len(levels),
                              figsize=(4 * len(levels), 3.5))
    if len(levels) == 1:
        axes = [axes]

    for ax, name in zip(axes, levels):
        hmap = feat_maps[name]
        # Normalize to [0, 1] for display
        hmap_norm = (hmap - hmap.min()) / (hmap.max() - hmap.min() + 1e-8)
        im = ax.imshow(hmap_norm, cmap='jet', aspect='auto',
                       vmin=0.0, vmax=1.0)
        ax.set_title(f'{name}', fontsize=11, fontweight='bold')
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

    fig.suptitle('A-FPN Feature Activation Heatmaps', fontsize=12)
    plt.tight_layout()
    st_module.pyplot(fig)
    plt.close(fig)
