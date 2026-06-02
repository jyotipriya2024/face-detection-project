# tests/features/detection/test_backbone.py
"""
Unit tests for LightFace-Net backbone, A-FPN, and DualHead.

Run:
    pytest tests/features/detection/ -v
"""

import pytest
import torch


class TestDepthwiseSeparableConv:
    def test_output_shape(self):
        from features.detection.backbone.depthwise_blocks import DepthwiseSeparableConv
        m = DepthwiseSeparableConv(in_ch=32, out_ch=64, stride=1)
        x = torch.randn(1, 32, 56, 56)
        out = m(x)
        assert out.shape == (1, 64, 56, 56)

    def test_stride_halves_spatial(self):
        from features.detection.backbone.depthwise_blocks import DepthwiseSeparableConv
        m = DepthwiseSeparableConv(in_ch=16, out_ch=32, stride=2)
        x = torch.randn(1, 16, 64, 64)
        assert m(x).shape == (1, 32, 32, 32)


class TestInvertedResidualBlock:
    def test_residual_skip_same_channels(self):
        from features.detection.backbone.depthwise_blocks import InvertedResidualBlock
        m = InvertedResidualBlock(in_ch=32, out_ch=32, stride=1, expand_ratio=6)
        x = torch.randn(1, 32, 28, 28)
        out = m(x)
        assert out.shape == x.shape  # residual path

    def test_no_residual_different_channels(self):
        from features.detection.backbone.depthwise_blocks import InvertedResidualBlock
        m = InvertedResidualBlock(in_ch=16, out_ch=32, stride=1, expand_ratio=6)
        x = torch.randn(1, 16, 28, 28)
        assert m(x).shape == (1, 32, 28, 28)


class TestChannelSpatialAttention:
    def test_output_matches_input_shape(self):
        from features.detection.backbone.attention import ChannelSpatialAttention
        m = ChannelSpatialAttention(channels=64)
        x = torch.randn(1, 64, 14, 14)
        assert m(x).shape == x.shape


class TestLightFaceNet:
    def test_forward_returns_three_scales(self):
        from features.detection.backbone.lightface_net import LightFaceNet
        net = LightFaceNet()
        x = torch.randn(1, 3, 256, 256)
        feats = net(x)
        assert set(feats.keys()) == {'P3', 'P4', 'P5'}

    def test_p3_stride8(self):
        from features.detection.backbone.lightface_net import LightFaceNet
        net = LightFaceNet()
        x = torch.randn(1, 3, 256, 256)
        feats = net(x)
        # P3 at stride 8
        assert feats['P3'].shape[2] == 256 // 8

    def test_parameter_count_under_5m(self):
        from features.detection.backbone.lightface_net import LightFaceNet
        net = LightFaceNet()
        n_params = sum(p.numel() for p in net.parameters())
        assert n_params < 5_000_000, f"Backbone too large: {n_params}"


class TestAsymmetricFPN:
    def test_output_channels_256(self):
        from features.detection.fpn.afpn import AsymmetricFPN, AFPNConfig
        afpn = AsymmetricFPN(AFPNConfig(c3=32, c4=160, c5=320, out=256))
        P3 = torch.randn(1, 32, 32, 32)
        P4 = torch.randn(1, 160, 16, 16)
        P5 = torch.randn(1, 320, 8, 8)
        out = afpn({'P3': P3, 'P4': P4, 'P5': P5})
        for key in ('F3', 'F4', 'F5'):
            assert out[key].shape[1] == 256, f"{key} should have 256 channels"

    def test_alpha_weights_are_learned(self):
        from features.detection.fpn.afpn import AsymmetricFPN, AFPNConfig
        afpn = AsymmetricFPN(AFPNConfig())
        # alpha3 and alpha4 should be nn.Parameter
        assert hasattr(afpn, 'alpha3')
        assert hasattr(afpn, 'alpha4')


class TestDualHead:
    def test_output_keys(self):
        from features.detection.head.dual_head import DualHead, HeadConfig
        head = DualHead(HeadConfig(in_channels=256, num_anchors=4, num_convs=2))
        feats = [torch.randn(1, 256, 32, 32)]
        out = head(feats)
        assert 'cls' in out and 'reg' in out

    def test_reg_output_4_coords(self):
        from features.detection.head.dual_head import DualHead, HeadConfig
        head = DualHead(HeadConfig(in_channels=256, num_anchors=4, num_convs=2))
        feats = [torch.randn(1, 256, 8, 8)]
        out = head(feats)
        B, NA, C = out['reg'].shape
        assert C == 4, "Regression head must output 4 coords"
