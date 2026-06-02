# features/detection/backbone/attention.py
"""
Channel-Spatial Attention module for LightFace-Net.
Fuses both channel importance and spatial saliency into a unified gate.
"""

import torch
import torch.nn as nn


class ChannelAttention(nn.Module):
    """Squeeze-excitation style channel attention."""

    def __init__(self, channels: int, reduction: int = 8):
        super().__init__()
        r = max(1, channels // reduction)
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc = nn.Sequential(
            nn.Conv2d(channels, r, 1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(r, channels, 1, bias=False),
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        avg_out = self.fc(self.avg_pool(x))
        max_out = self.fc(self.max_pool(x))
        return self.sigmoid(avg_out + max_out)


class SpatialAttention(nn.Module):
    """Spatial attention via channel-wise max and avg pooling."""

    def __init__(self, kernel_size: int = 7):
        super().__init__()
        padding = kernel_size // 2
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=padding, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        concat = torch.cat([avg_out, max_out], dim=1)
        return self.sigmoid(self.conv(concat))


class ChannelSpatialAttention(nn.Module):
    """
    CBAM-style sequential channel + spatial attention.
    Applied at P3/P4/P5 extraction points in the backbone.
    """

    def __init__(self, channels: int, reduction: int = 8):
        super().__init__()
        self.channel_attn = ChannelAttention(channels, reduction)
        self.spatial_attn = SpatialAttention()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x * self.channel_attn(x)
        x = x * self.spatial_attn(x)
        return x
