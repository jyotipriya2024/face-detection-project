# features/detection/backbone/lightface_net.py
"""
LightFace-Net: Lightweight depthwise separable backbone for real-time face detection.

Architecture summary:
  - Stem conv (3 → 32, stride 2)
  - 11 Inverted Residual stages yielding channel depths [16,24,32,64,96,160,320]
  - Channel-Spatial Attention applied at P3 (stage 3), P4 (stage 6), P5 (stage 10)
  - Returns {'P3': tensor, 'P4': tensor, 'P5': tensor} for A-FPN consumption

FLOPs: ~140 MFLOPs at 640×480 input
Parameters: ~1.0 M (FP32) → ~250 KB (INT8)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import torch
import torch.nn as nn

from .depthwise_blocks import BlockConfig, InvertedResidualBlock
from .attention import ChannelSpatialAttention


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class StageConfig:
    in_channels: int
    out_channels: int
    num_blocks: int
    stride: int
    expand_ratio: int = 6


@dataclass
class BackboneConfig:
    """All architecture hyperparameters for LightFace-Net."""
    stage_configs: List[StageConfig] = field(default_factory=lambda: [
        StageConfig(32,  16,  1, 1, 1),   # stage 0
        StageConfig(16,  24,  2, 2, 6),   # stage 1
        StageConfig(24,  32,  3, 2, 6),   # stage 2  → P3 (stride-8)
        StageConfig(32,  64,  4, 2, 6),   # stage 3
        StageConfig(64,  96,  3, 1, 6),   # stage 4
        StageConfig(96,  160, 3, 2, 6),   # stage 5  → P4 (stride-16)
        StageConfig(160, 320, 1, 1, 6),   # stage 6  → P5 (stride-32)
    ])
    attention_channels: List[int] = field(default_factory=lambda: [32, 160, 320])


# ---------------------------------------------------------------------------
# Stage builder
# ---------------------------------------------------------------------------

def _build_stage(cfg: StageConfig) -> nn.Sequential:
    blocks: list[nn.Module] = []
    for i in range(cfg.num_blocks):
        block_cfg = BlockConfig(
            in_channels=cfg.in_channels if i == 0 else cfg.out_channels,
            out_channels=cfg.out_channels,
            stride=cfg.stride if i == 0 else 1,
            expand_ratio=cfg.expand_ratio,
        )
        blocks.append(InvertedResidualBlock(block_cfg))
    return nn.Sequential(*blocks)


# ---------------------------------------------------------------------------
# Backbone
# ---------------------------------------------------------------------------

class LightFaceNet(nn.Module):
    """
    LightFace-Net backbone.

    Returns multi-scale feature maps (P3, P4, P5) for consumption by A-FPN.

    Example:
        >>> model = LightFaceNet(BackboneConfig())
        >>> feats = model(torch.randn(1, 3, 640, 480))
        >>> feats['P3'].shape  # (1, 32, 80, 60)
        >>> feats['P4'].shape  # (1, 160, 40, 30)
        >>> feats['P5'].shape  # (1, 320, 20, 15)
    """

    # Indices (0-based) of stages whose output becomes P3, P4, P5
    _FPN_STAGES = {2: 'P3', 5: 'P4', 6: 'P5'}

    def __init__(self, config: BackboneConfig = BackboneConfig()):
        super().__init__()
        self.stem = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU6(inplace=True),
        )
        self.stages = nn.ModuleList(
            [_build_stage(sc) for sc in config.stage_configs]
        )
        # One attention module per FPN output stage
        p_channels = [sc.out_channels for i, sc in
                      enumerate(config.stage_configs) if i in self._FPN_STAGES]
        self.attention = nn.ModuleDict({
            name: ChannelSpatialAttention(ch)
            for name, ch in zip(['P3', 'P4', 'P5'], p_channels)
        })
        self._init_weights()

    def _init_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out',
                                        nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        x = self.stem(x)
        features: Dict[str, torch.Tensor] = {}
        for i, stage in enumerate(self.stages):
            x = stage(x)
            if i in self._FPN_STAGES:
                name = self._FPN_STAGES[i]
                features[name] = self.attention[name](x)
        return features   # {'P3': tensor, 'P4': tensor, 'P5': tensor}
