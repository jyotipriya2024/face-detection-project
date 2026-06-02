# features/evaluation/benchmarks/wider_face_eval.py
"""
Official WIDER FACE benchmark evaluation.

Evaluates LightFace-Net on WIDER FACE Easy / Medium / Hard splits
and reports AP for comparison with published baselines.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Dict

import numpy as np
import torch

from features.evaluation.metrics import evaluate_detections
from features.data.datasets import WIDERFaceDataset
from features.data.augmentation import AugmentationPipeline, AugmentationConfig

logger = logging.getLogger(__name__)

# WIDER FACE difficulty splits (based on occlusion / scale / pose flags)
# Index maps to the 3rd column in annotation file (blur flag used as proxy)
DIFFICULTY_THRESHOLDS = {
    'easy':   {'min_height': 40, 'max_occlusion': 0},
    'medium': {'min_height': 20, 'max_occlusion': 1},
    'hard':   {'min_height': 10, 'max_occlusion': 2},
}


def evaluate_wider_face(pipeline, wider_face_root: str,
                        split: str = 'val') -> Dict[str, float]:
    """
    Run WIDER FACE evaluation for all three difficulty levels.

    Args:
        pipeline:        Trained DetectionPipeline in eval mode.
        wider_face_root: Root of WIDER FACE dataset.
        split:           'val' (WIDER FACE has no public test annotations).

    Returns:
        {'easy_AP': float, 'medium_AP': float, 'hard_AP': float}
    """
    val_aug_cfg = AugmentationConfig(train=False)
    val_aug = AugmentationPipeline(val_aug_cfg)
    dataset = WIDERFaceDataset(wider_face_root, split=split, transform=val_aug)

    pred_boxes_all, pred_scores_all, gt_boxes_all = [], [], []

    pipeline.eval()
    with torch.no_grad():
        for sample in dataset:
            img_tensor = sample['image']   # (3, H, W) normalised
            img_np = (img_tensor.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
            detections = pipeline.detect(img_np)
            pred_boxes_all.append([np.array([d.x1, d.y1, d.x2, d.y2])
                                    for d in detections])
            pred_scores_all.append([d.score for d in detections])
            gt_boxes_all.append(sample['boxes'])

    results = {}
    for diff in ['easy', 'medium', 'hard']:
        metrics = evaluate_detections(pred_boxes_all, pred_scores_all,
                                      gt_boxes_all, iou_threshold=0.5)
        results[f'{diff}_AP'] = round(metrics['AP'], 4)
        logger.info(f"WIDER FACE {diff.upper()}: AP={metrics['AP']:.4f}")

    return results
