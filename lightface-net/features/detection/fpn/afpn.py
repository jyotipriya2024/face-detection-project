# features/detection/fpn/afpn.py
"""
Asymmetric Feature Pyramid Network (A-FPN) for LightFace-Net.

Key difference from standard FPN:
  - Learnable per-scale alpha weights govern semantic-spatial blending
  - Higher alpha at P3 → preserve fine-grained spatial detail for tiny faces
  - Top-down lateral convolutions align channel dims before merging

Inputs:  {'P3': (B,C3,H3,W3), 'P4': (B,C4,H4,W4), 'P5': (B,C5,H5,W5)}
Outputs: {'F3': tensor, 'F4': tensor, 'F5': tensor}  — all 256 channels
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import torch
import torch.nn as nn
import torch.nn.functional as F

from .attention_weights import ScaleAwareAttention


@dataclass
class AFPNConfig:
    c3_channels: int = 32
    c4_channels: int = 160
    c5_channels: int = 320
    out_channels: int = 256


class AsymmetricFPN(nn.Module):
    """
    A-FPN: scale-aware spatial-semantic top-down fusion.

    Example:
        >>> afpn = AsymmetricFPN(AFPNConfig())
        >>> feats = afpn({'P3': torch.randn(1,32,80,60),
        ...               'P4': torch.randn(1,160,40,30),
        ...               'P5': torch.randn(1,320,20,15)})
        >>> feats['F3'].shape  # (1, 256, 80, 60)
    """

    def __init__(self, cfg: AFPNConfig = AFPNConfig()):
        super().__init__()
        C = cfg.out_channels

        # Lateral 1×1 convolutions to project backbone channels → C
        self.lat5 = self._lateral(cfg.c5_channels, C)
        self.lat4 = self._lateral(cfg.c4_channels, C)
        self.lat3 = self._lateral(cfg.c3_channels, C)

        # Output 3×3 smoothing convolutions
        self.smooth4 = self._smooth(C)
        self.smooth3 = self._smooth(C)

        # Scale-aware attention gates
        self.alpha4 = ScaleAwareAttention(C)
        self.alpha3 = ScaleAwareAttention(C)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _lateral(in_ch: int, out_ch: int) -> nn.Sequential:
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    @staticmethod
    def _smooth(channels: int) -> nn.Sequential:
        return nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True),
        )

    @staticmethod
    def _upsample(src: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Bilinear upsample src to match target's spatial size."""
        return F.interpolate(src, size=target.shape[-2:],
                             mode='bilinear', align_corners=False)

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(self, backbone_features: Dict[str, torch.Tensor]
                ) -> Dict[str, torch.Tensor]:
        P3 = backbone_features['P3']
        P4 = backbone_features['P4']
        P5 = backbone_features['P5']

        # Project backbone features to common channel dim C
        L5 = self.lat5(P5)
        L4 = self.lat4(P4)
        L3 = self.lat3(P3)

        # Top-down path with asymmetric attention blending
        F5 = L5                                                # (B, C, H5, W5)

        alpha4 = self.alpha4(L4)                              # (B, 1, H4, W4)
        F4_raw = alpha4 * L4 + (1 - alpha4) * self._upsample(F5, L4)
        F4 = self.smooth4(F4_raw)                             # (B, C, H4, W4)

        alpha3 = self.alpha3(L3)                              # (B, 1, H3, W3)
        F3_raw = alpha3 * L3 + (1 - alpha3) * self._upsample(F4, L3)
        F3 = self.smooth3(F3_raw)                             # (B, C, H3, W3)

        return {'F3': F3, 'F4': F4, 'F5': F5}
