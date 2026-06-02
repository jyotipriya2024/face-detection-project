# shared/visualization.py
"""
Visualization utilities: draw bounding boxes, PR curves, A-FPN heatmaps.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np


# -------------------------------------------------------------------------
# Bounding box drawing
# -------------------------------------------------------------------------

def draw_detections(image: np.ndarray,
                    boxes: List[Tuple[float, float, float, float]],
                    scores: Optional[List[float]] = None,
                    color: Tuple[int, int, int] = (0, 255, 0),
                    thickness: int = 2,
                    font_scale: float = 0.55) -> np.ndarray:
    """
    Draw bounding boxes on a BGR image.

    Args:
        image:  BGR image (HxWx3 uint8).
        boxes:  List of (x1, y1, x2, y2) in pixel coords.
        scores: Optional confidence scores for labels.
        color:  BGR draw color.

    Returns:
        Annotated copy of the image.
    """
    out = image.copy()
    for i, (x1, y1, x2, y2) in enumerate(boxes):
        pt1 = (int(x1), int(y1))
        pt2 = (int(x2), int(y2))
        cv2.rectangle(out, pt1, pt2, color, thickness)
        if scores:
            label = f'{scores[i]:.2f}'
            cv2.putText(out, label, (int(x1), max(int(y1) - 6, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1,
                        cv2.LINE_AA)
    return out


# -------------------------------------------------------------------------
# FPS overlay
# -------------------------------------------------------------------------

def draw_fps_overlay(image: np.ndarray, fps: float) -> np.ndarray:
    out = image.copy()
    label = f'FPS: {fps:.1f}'
    cv2.putText(out, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 255, 255), 2, cv2.LINE_AA)
    return out


# -------------------------------------------------------------------------
# PR curve
# -------------------------------------------------------------------------

def plot_pr_curve(precision: np.ndarray, recall: np.ndarray,
                  ap: float, title: str = 'PR Curve',
                  save_path: Optional[str] = None) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(recall, precision, linewidth=2, color='royalblue')
    ax.fill_between(recall, precision, alpha=0.15, color='royalblue')
    ax.set_xlabel('Recall', fontsize=13)
    ax.set_ylabel('Precision', fontsize=13)
    ax.set_title(f'{title}  (AP={ap:.4f})', fontsize=14)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.05)
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


# -------------------------------------------------------------------------
# A-FPN feature heatmap
# -------------------------------------------------------------------------

def visualize_fpn_heatmap(feat_maps: Dict[str, np.ndarray],
                           save_path: Optional[str] = None) -> None:
    """
    Visualize A-FPN feature activation heatmaps at P3, P4, P5.

    Args:
        feat_maps: {'F3': (H3,W3), 'F4': (H4,W4), 'F5': (H5,W5)} — 2-D mean maps.
        save_path: If provided, save the figure to this path.
    """
    levels = list(feat_maps.keys())
    fig, axes = plt.subplots(1, len(levels), figsize=(5 * len(levels), 4))
    if len(levels) == 1:
        axes = [axes]

    for ax, name in zip(axes, levels):
        hmap = feat_maps[name]
        im = ax.imshow(hmap, cmap='jet', aspect='auto')
        ax.set_title(f'A-FPN {name}', fontsize=12)
        ax.axis('off')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle('Asymmetric FPN Feature Activation Maps', fontsize=14)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def extract_fpn_heatmaps(pipeline,
                          bgr_frame: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Extract per-level mean activation maps from a frame.

    Args:
        pipeline:   DetectionPipeline (must expose .afpn).
        bgr_frame:  Input BGR image.

    Returns:
        {'F3': ndarray(H,W), 'F4': ndarray, 'F5': ndarray}
    """
    import torch
    from shared.image_ops import bgr_to_tensor

    tensor = bgr_to_tensor(bgr_frame).to(next(pipeline.parameters()).device)
    with torch.no_grad():
        backbone_feats = pipeline.backbone(tensor)
        fpn_feats = pipeline.afpn(backbone_feats)

    heatmaps = {}
    for name, feat in fpn_feats.items():
        # Mean across channels → (H, W)
        heatmaps[name] = feat[0].mean(0).cpu().numpy()
    return heatmaps
