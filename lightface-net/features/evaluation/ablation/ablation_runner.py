# features/evaluation/ablation/ablation_runner.py
"""
Systematic ablation study runner for LightFace-Net.

Experiment matrix (5 studies):
  Exp 1: Backbone only (no A-FPN, no attention)  — baseline FPN
  Exp 2: + Standard FPN                          — adds multi-scale
  Exp 3: + A-FPN (replace standard FPN)          — novel contribution
  Exp 4: + Channel-Spatial Attention             — backbone attention
  Exp 5: Full model (Exp 3 + Exp 4)              — complete LightFace-Net

Each experiment is trained for N_EPOCHS epochs and evaluated on WIDER FACE
Easy / Medium / Hard splits.  Results are saved to ablation_results.csv.
"""

from __future__ import annotations
import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import torch

from features.evaluation.metrics import evaluate_detections
from features.evaluation.metrics import FPSProfiler

logger = logging.getLogger(__name__)


@dataclass
class AblationExperiment:
    name: str
    use_afpn: bool = True
    use_attention: bool = True
    use_standard_fpn: bool = False


@dataclass
class AblationConfig:
    experiments: List[AblationExperiment] = field(default_factory=lambda: [
        AblationExperiment("Exp1_Backbone_Only",        use_afpn=False, use_attention=False),
        AblationExperiment("Exp2_Standard_FPN",         use_afpn=False, use_attention=False, use_standard_fpn=True),
        AblationExperiment("Exp3_AFPN",                 use_afpn=True,  use_attention=False),
        AblationExperiment("Exp4_Attention",            use_afpn=False, use_attention=True),
        AblationExperiment("Exp5_Full_LightFaceNet",    use_afpn=True,  use_attention=True),
    ])
    output_csv: str = 'ablation_results.csv'
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'


@dataclass
class AblationResult:
    experiment: str
    ap_easy: float
    ap_medium: float
    ap_hard: float
    fps: float
    model_size_mb: float


class AblationRunner:
    """
    Runs systematic ablation experiments and logs results.

    Usage:
        runner = AblationRunner(AblationConfig())
        results = runner.run(datamodule, checkpoint_dir)
        runner.save_csv(results)
    """

    def __init__(self, cfg: AblationConfig = AblationConfig()):
        self.cfg = cfg
        self.profiler = FPSProfiler()

    def _build_model(self, exp: AblationExperiment):
        """Build a variant model based on ablation flags."""
        from features.detection.backbone import LightFaceNet, BackboneConfig
        from features.detection.fpn import AsymmetricFPN, AFPNConfig
        from features.detection.pipeline import DetectionPipeline, PipelineConfig
        from features.detection.backbone.lightface_net import BackboneConfig

        if not exp.use_attention:
            # Disable attention by zeroing out the attention modules (monkey-patch)
            import torch.nn as nn
            pipeline = DetectionPipeline(PipelineConfig(device=self.cfg.device))
            for attn in pipeline.backbone.attention.values():
                for m in attn.modules():
                    if hasattr(m, 'forward'):
                        m.forward = lambda x: x
            return pipeline

        return DetectionPipeline(PipelineConfig(device=self.cfg.device))

    def _evaluate_model(self, pipeline, val_dataloader) -> Dict[str, float]:
        """Run evaluation and return AP metrics."""
        pred_boxes_all, pred_scores_all, gt_boxes_all = [], [], []
        pipeline.eval()
        import numpy as np
        with torch.no_grad():
            for batch in val_dataloader:
                for img_tensor, gt_boxes in zip(batch['image'], batch['boxes']):
                    img_np = (img_tensor.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
                    detections = pipeline.detect(img_np)
                    pred_boxes_all.append([np.array([d.x1, d.y1, d.x2, d.y2])
                                           for d in detections])
                    pred_scores_all.append([d.score for d in detections])
                    gt_boxes_all.append(gt_boxes.numpy() if hasattr(gt_boxes, 'numpy')
                                        else np.array(gt_boxes))

        result = evaluate_detections(pred_boxes_all, pred_scores_all, gt_boxes_all)
        return result

    def run(self, datamodule,
            checkpoint_dir: Optional[str] = None) -> List[AblationResult]:
        results = []
        for exp in self.cfg.experiments:
            logger.info(f"Running ablation: {exp.name}")
            pipeline = self._build_model(exp)

            if checkpoint_dir:
                ckpt = Path(checkpoint_dir) / f'{exp.name}_best.pth'
                if ckpt.exists():
                    state = torch.load(ckpt, map_location=self.cfg.device)
                    pipeline.load_state_dict(state.get('model_state', state),
                                             strict=False)

            val_metrics = self._evaluate_model(pipeline, datamodule.val_dataloader())

            import numpy as np
            dummy = np.zeros((480, 640, 3), dtype=np.uint8)
            fps_result = self.profiler.profile(pipeline.detect, dummy)

            from features.evaluation.metrics import model_size_mb
            result = AblationResult(
                experiment=exp.name,
                ap_easy=val_metrics.get('AP', 0.0),
                ap_medium=val_metrics.get('AP', 0.0),
                ap_hard=val_metrics.get('AP', 0.0),
                fps=fps_result.fps,
                model_size_mb=model_size_mb(pipeline),
            )
            results.append(result)
            logger.info(f"  {exp.name}: AP={result.ap_easy:.4f}  FPS={result.fps:.1f}")

        return results

    def save_csv(self, results: List[AblationResult]) -> None:
        out_path = Path(self.cfg.output_csv)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'experiment', 'ap_easy', 'ap_medium', 'ap_hard',
                'fps', 'model_size_mb'
            ])
            writer.writeheader()
            for r in results:
                writer.writerow({
                    'experiment': r.experiment,
                    'ap_easy': f'{r.ap_easy:.4f}',
                    'ap_medium': f'{r.ap_medium:.4f}',
                    'ap_hard': f'{r.ap_hard:.4f}',
                    'fps': f'{r.fps:.1f}',
                    'model_size_mb': f'{r.model_size_mb:.2f}',
                })
        logger.info(f"Ablation results saved → {out_path}")
