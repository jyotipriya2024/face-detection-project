# shared/constants.py
"""
Project-wide constants: normalization params, anchor design values, etc.
Never import model or dataset classes here — keep this dependency-free.
"""

# ImageNet normalization (used for pre-processing)
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD  = (0.229, 0.224, 0.225)

# Anchor design
ANCHOR_STRIDES       = [8, 16, 32]           # Feature map strides (P3/P4/P5)
ANCHOR_BASE_SIZES    = [[16, 32], [64, 128], [256, 512]]
ANCHOR_ASPECT_RATIOS = [1.0, 1.5]            # Width-to-height ratios

# Training defaults
DEFAULT_INPUT_SIZE    = (640, 480)           # (W, H)
DEFAULT_BATCH_SIZE    = 32
DEFAULT_NUM_EPOCHS    = 120
DEFAULT_LR            = 1e-3
DEFAULT_WEIGHT_DECAY  = 5e-4

# Evaluation
IOU_THRESHOLD         = 0.5
SCORE_THRESHOLD       = 0.3
NMS_IOU_THRESHOLD     = 0.45
MAX_DETECTIONS        = 300

# Model footprint targets
TARGET_MODEL_SIZE_MB  = 10.0               # INT8 target
TARGET_FPS_JETSON     = 30.0

# Compression
PRUNE_THRESHOLD_PERCENTILE = 0.50          # Remove bottom 50% of BN gammas
SPARSITY_LAMBDA            = 1e-4
INT8_NUM_CALIBRATION_IMGS  = 1024

# Supported datasets
SUPPORTED_DATASETS = ['wider_face', 'fddb', 'lfw']
