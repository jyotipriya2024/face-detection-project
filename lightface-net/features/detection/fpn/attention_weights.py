# features/detection/fpn/attention_weights.py
"""
Scale-aware attention weight module for Asymmetric FPN.
Produces per-scale learnable alpha weights in [0,1] that control
the semantic-vs-spatial blending at each pyramid level.
"""

import torch
import torch.nn as nn


class ScaleAwareAttention(nn.Module):
    """
    Produces a spatial attention map alpha ∈ (0,1) for a given feature level.
    Used in A-FPN to weight the skip connection vs up-sampled signal:

        F_out = alpha * F_skip + (1 - alpha) * F_upsampled

    A small 1×1 conv + sigmoid is used to keep the module parameter-light.
    """

    def __init__(self, in_channels: int):
        super().__init__()
        self.gate = nn.Sequential(
            nn.Conv2d(in_channels, in_channels // 2, 1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels // 2, 1, 1, bias=False),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Return spatial weight map with shape (B, 1, H, W)."""
        return self.gate(x)
