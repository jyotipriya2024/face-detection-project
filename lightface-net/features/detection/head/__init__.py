# features/detection/head/__init__.py
from .dual_head import DualHead, HeadConfig
from .anchor_generator import AnchorGenerator, AnchorConfig
from .nms import apply_nms, NMSConfig

__all__ = [
    "DualHead", "HeadConfig",
    "AnchorGenerator", "AnchorConfig",
    "apply_nms", "NMSConfig",
]
