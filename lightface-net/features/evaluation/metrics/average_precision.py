# features/evaluation/metrics/average_precision.py
"""
Average Precision (AP) computation at IoU=0.5.

Implements the PASCAL VOC 2010+ interpolated AP metric used in
WIDER FACE benchmark evaluation.
"""

from __future__ import annotations
from typing import List

import numpy as np


def compute_iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    """IoU between two boxes (x1,y1,x2,y2)."""
    ix1 = max(box_a[0], box_b[0])
    iy1 = max(box_a[1], box_b[1])
    ix2 = min(box_a[2], box_b[2])
    iy2 = min(box_a[3], box_b[3])
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    b_area = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    return inter / max(a_area + b_area - inter, 1e-6)


def compute_ap(precision: np.ndarray, recall: np.ndarray) -> float:
    """
    Interpolated Average Precision (101-point interpolation).
    """
    # Append sentinel values
    mrec = np.concatenate([[0.0], recall, [1.0]])
    mpre = np.concatenate([[0.0], precision, [0.0]])
    # Monotonically decreasing precision
    for i in range(len(mpre) - 2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i + 1])
    recall_thresholds = np.linspace(0, 1, 101)
    ap = float(np.mean([
        mpre[np.searchsorted(mrec, t, side='left') - 1]
        for t in recall_thresholds
    ]))
    return ap


def evaluate_detections(
    pred_boxes_all: List[List[np.ndarray]],
    pred_scores_all: List[List[float]],
    gt_boxes_all: List[np.ndarray],
    iou_threshold: float = 0.5,
) -> dict:
    """
    Compute precision, recall, and AP across a dataset.

    Args:
        pred_boxes_all:  List of predicted boxes per image [(N_i,4) arrays].
        pred_scores_all: List of confidence scores per image.
        gt_boxes_all:    List of ground-truth boxes per image [(M_i,4) arrays].
        iou_threshold:   IoU threshold for a TP.

    Returns:
        {'AP': float, 'precision': array, 'recall': array}
    """
    # Flatten all predictions with image index
    all_preds = []
    for i, (boxes, scores) in enumerate(zip(pred_boxes_all, pred_scores_all)):
        for b, s in zip(boxes, scores):
            all_preds.append((s, i, b))
    all_preds.sort(key=lambda x: -x[0])   # sort by confidence descending

    n_gt = sum(len(g) for g in gt_boxes_all)
    matched = [np.zeros(len(g), dtype=bool) for g in gt_boxes_all]

    tp_list, fp_list = [], []
    for score, img_idx, pred_box in all_preds:
        gts = gt_boxes_all[img_idx]
        best_iou, best_j = 0.0, -1
        for j, gt in enumerate(gts):
            iou = compute_iou(pred_box, gt)
            if iou > best_iou:
                best_iou, best_j = iou, j
        if best_iou >= iou_threshold and best_j >= 0 and not matched[img_idx][best_j]:
            tp_list.append(1)
            fp_list.append(0)
            matched[img_idx][best_j] = True
        else:
            tp_list.append(0)
            fp_list.append(1)

    tp_cumsum = np.cumsum(tp_list)
    fp_cumsum = np.cumsum(fp_list)
    recall = tp_cumsum / max(n_gt, 1)
    precision = tp_cumsum / np.maximum(tp_cumsum + fp_cumsum, 1)

    ap = compute_ap(precision, recall)
    return {'AP': ap, 'precision': precision, 'recall': recall}
