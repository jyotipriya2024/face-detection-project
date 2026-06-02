# features/detection/__init__.py
from .pipeline import DetectionPipeline, PipelineConfig, BoundingBox
from .backbone import LightFaceNet, BackboneConfig
from .fpn import AsymmetricFPN, AFPNConfig
from .head import DualHead, HeadConfig

__all__ = [
    "DetectionPipeline", "PipelineConfig", "BoundingBox",
    "LightFaceNet", "BackboneConfig",
    "AsymmetricFPN", "AFPNConfig",
    "DualHead", "HeadConfig",
]
