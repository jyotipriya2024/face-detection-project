# apps/benchmark_runner/run_benchmark.py
"""
Standalone benchmark CLI.

Usage:
    python apps/benchmark_runner/run_benchmark.py \
        --config infrastructure/config/model_config.yaml \
        --checkpoint models/checkpoints/best.pth \
        --output benchmark_results.json

Outputs:
    - FPS / latency at multiple resolutions
    - Model size report
    - Per-resolution JSON artifact
"""

from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import torch
from features.detection.pipeline import DetectionPipeline
from features.evaluation.benchmarks.hardware_eval import (
    run_hardware_benchmark, HardwareBenchmarkConfig
)
from features.evaluation.metrics import model_size_mb

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='LightFace-Net Benchmark Runner')
    parser.add_argument('--config', type=str,
                        default='infrastructure/config/model_config.yaml')
    parser.add_argument('--checkpoint', type=str, default=None)
    parser.add_argument('--output', type=str, default='benchmark_results.json')
    parser.add_argument('--warmup', type=int, default=20)
    parser.add_argument('--runs', type=int, default=200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Load pipeline
    if Path(args.config).exists():
        pipeline = DetectionPipeline.from_config(args.config)
    else:
        logger.warning(f"Config not found at {args.config} — using defaults.")
        pipeline = DetectionPipeline()

    if args.checkpoint and Path(args.checkpoint).exists():
        state = torch.load(args.checkpoint, map_location=pipeline.device)
        pipeline.load_state_dict(state.get('model_state', state), strict=False)
        logger.info(f"Loaded checkpoint: {args.checkpoint}")

    logger.info(f"Model size: {model_size_mb(pipeline):.2f} MB")

    # Run benchmark
    cfg = HardwareBenchmarkConfig(
        warmup_runs=args.warmup,
        benchmark_runs=args.runs,
        output_json=args.output,
    )
    results = run_hardware_benchmark(pipeline, cfg)

    # Pretty print summary
    print("\n" + "=" * 60)
    print("  LightFace-Net Hardware Benchmark Results")
    print("=" * 60)
    for res_key, metrics in results.get('resolutions', {}).items():
        print(f"  {res_key:>10}:  "
              f"FPS={metrics['fps']:>6.1f}  "
              f"Latency={metrics['latency_mean_ms']:>7.2f} ms  "
              f"Size={metrics['model_size_mb']:>6.2f} MB")
    print("=" * 60)
    print(f"  Full results saved → {args.output}")


if __name__ == '__main__':
    main()
