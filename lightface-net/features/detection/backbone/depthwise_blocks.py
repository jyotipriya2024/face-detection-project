# features/detection/backbone/depthwise_blocks.py
"""
Depthwise Separable Convolution building blocks for LightFace-Net.
Provides 9x FLOPs reduction over standard convolutions at minimal accuracy cost.
"""

import torch
import torch.nn as nn
from dataclasses import dataclass
from typing import Optional


@dataclass
class BlockConfig:
    in_channels: int
    out_channels: int
    stride: int = 1
    expand_ratio: int = 6
    use_se: bool = False


class DepthwiseSeparableConv(nn.Module):
    """Standard depthwise separable convolution: DW-Conv + PW-Conv."""

    def __init__(self, in_channels: int, out_channels: int,
                 stride: int = 1, padding: int = 1):
        super().__init__()
        self.dw = nn.Sequential(
            nn.Conv2d(in_channels, in_channels, 3, stride=stride,
                      padding=padding, groups=in_channels, bias=False),
            nn.BatchNorm2d(in_channels),
            nn.ReLU6(inplace=True),
        )
        self.pw = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU6(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.pw(self.dw(x))


class InvertedResidualBlock(nn.Module):
    """
    MobileNetV2-style inverted residual block (bottleneck).
    Expands channels, applies DW conv, then projects back.
    Residual connection only when spatial size is preserved.
    """

    def __init__(self, cfg: BlockConfig):
        super().__init__()
        hidden = int(cfg.in_channels * cfg.expand_ratio)
        self.use_residual = (cfg.stride == 1 and
                             cfg.in_channels == cfg.out_channels)
        layers: list[nn.Module] = []
        if cfg.expand_ratio != 1:
            layers += [
                nn.Conv2d(cfg.in_channels, hidden, 1, bias=False),
                nn.BatchNorm2d(hidden),
                nn.ReLU6(inplace=True),
            ]
        layers += [
            nn.Conv2d(hidden, hidden, 3, stride=cfg.stride, padding=1,
                      groups=hidden, bias=False),
            nn.BatchNorm2d(hidden),
            nn.ReLU6(inplace=True),
            nn.Conv2d(hidden, cfg.out_channels, 1, bias=False),
            nn.BatchNorm2d(cfg.out_channels),
        ]
        self.conv = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.conv(x)
        return out + x if self.use_residual else out


class SqueezeExcitation(nn.Module):
    """Lightweight channel-wise attention via squeeze-and-excitation."""

    def __init__(self, channels: int, reduction: int = 4):
        super().__init__()
        squeezed = max(1, channels // reduction)
        self.se = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(channels, squeezed, 1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(squeezed, channels, 1, bias=False),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.se(x)
