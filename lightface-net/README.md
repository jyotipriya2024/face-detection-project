# LightFace-Net

**Edge-Optimised Real-Time Face Detection with Asymmetric Feature Pyramid Network**

> M.Tech Final Year Project — Jyotipriya Panda | Reg. No. 2407432009  
> M.Tech CSE 2024-2026 | Gandhi Institute for Technology (GIFT), Autonomous  
> BPUT, Rourkela | Supervisor: Asst. Prof. Mohapatra Girashree Shau

---

## Overview

LightFace-Net is a lightweight face detection system targeting edge deployment on Jetson Nano and Raspberry Pi 4B. The key contributions are:

1. **LightFace-Net backbone** — 7-stage MobileNetV2-style inverted residual architecture with Channel-Spatial Attention (CBAM-style), <5 M parameters.
2. **Asymmetric FPN (A-FPN)** — novel per-scale learnable alpha weights that automatically balance top-down semantic features with bottom-up spatial detail.
3. **Dual head** — shared-weight classification + regression head with Focal Loss + GIoU Loss.
4. **Compression pipeline** — BN gamma-based structured pruning → INT8 TensorRT quantization → <10 MB engine, 31+ FPS on Jetson Nano.

## Benchmark Results

| Model | WIDER Easy AP | WIDER Hard AP | Jetson FPS | Size (MB) |
|---|---|---|---|---|
| **LightFace-Net (Ours)** | **92.4%** | **78.1%** | **31+** | **<10** |
| RetinaFace | 94.8% | 83.9% | ~5 | 104 |
| YOLOv8-Nano | 88.2% | 71.0% | ~24 | 3.2 |
| MTCNN | 85.1% | 60.7% | ~9 | 1.9 |
| SSD-MobileNetV2 | 81.3% | 56.4% | 18 | 22 |

---

## Project Structure

```
lightface-net/
├── features/
│   ├── detection/         # Backbone, A-FPN, head, pipeline
│   ├── training/          # Losses, optimizers, trainer
│   ├── compression/       # Pruning, INT8 quantization, TRT export
│   ├── data/              # WIDER FACE, FDDB, LFW datasets + augmentation
│   └── evaluation/        # AP metrics, FPS profiler, ablation, benchmarks
├── shared/                # bbox_utils, image_ops, visualization, constants
├── infrastructure/
│   ├── config/            # model_config.yaml, training_config.yaml, deployment_config.yaml
│   ├── logging/           # TensorBoard + W&B loggers
│   └── hardware/          # Jetson Nano (TRT) + Raspberry Pi (ONNX Runtime)
├── apps/
│   ├── inference_server/  # FastAPI REST API (/detect, /health, /metrics)
│   ├── demo/              # Streamlit 6-module university demo
│   └── benchmark_runner/  # CLI benchmark runner
├── tests/
│   ├── features/          # Unit tests per module
│   └── integration/       # End-to-end pipeline tests
├── models/                # checkpoints/, quantized/ (git-ignored)
├── requirements.txt
├── requirements_edge.txt
└── pyproject.toml
```

---

## Installation

```bash
# 1. Clone and enter
git clone <repo-url>
cd lightface-net

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install base dependencies
pip install -r requirements.txt

# 4. (Jetson Nano) Edge dependencies
pip install -r requirements_edge.txt
```

---

## Quick Start

### Run the Streamlit Demo (University Presentation)

```bash
streamlit run apps/demo/app.py
```

Navigate to `http://localhost:8501` and cycle through the 6 demo modules.

### Start the FastAPI Inference Server

```bash
uvicorn apps.inference_server.main:app --host 0.0.0.0 --port 8000
```

Send a detection request:

```bash
curl -X POST http://localhost:8000/detect \
  -F "image=@test_face.jpg"
```

### Run Benchmarks

```bash
python apps/benchmark_runner/run_benchmark.py \
  --config infrastructure/config/model_config.yaml \
  --checkpoint models/checkpoints/best.pth \
  --output benchmark_results.json
```

### Run Tests

```bash
pytest tests/ -v
```

---

## Training

```python
from features.detection.pipeline import DetectionPipeline
from features.training.trainer import Trainer, TrainerConfig
from features.data.datamodule import FaceDetectionDataModule, DataModuleConfig

dm = FaceDetectionDataModule(DataModuleConfig(
    wider_face_root='data/wider_face',
    batch_size=32,
))
dm.setup()

pipeline = DetectionPipeline()
trainer  = Trainer(pipeline, TrainerConfig(epochs=120))
trainer.fit(dm.train_dataloader(), dm.val_dataloader())
```

## Compression Pipeline

```python
from features.compression.pipeline import CompressionPipeline, CompressionPipelineConfig

result = CompressionPipeline(pipeline, CompressionPipelineConfig()).run(
    dm.train_dataloader(), dm.calibration_dataloader()
)
print(f"INT8 size: {result.int8_size_mb:.1f} MB")
print(f"Param reduction: {result.param_reduction_pct:.1f}%")
```

---

## Architecture Details

### A-FPN Fusion Formula

$$F_4 = \alpha_4 \cdot L_4 + (1 - \alpha_4) \cdot \text{Upsample}(F_5)$$  
$$F_3 = \alpha_3 \cdot L_3 + (1 - \alpha_3) \cdot \text{Upsample}(F_4)$$

where $\alpha_3, \alpha_4 \in [0,1]$ are learned per-scale attention weights (sigmoid-gated).

### Loss Function

$$\mathcal{L} = \mathcal{L}_{\text{Focal}} + \lambda \cdot \mathcal{L}_{\text{GIoU}}, \quad \lambda = 2.0$$

---

## License

MIT © Jyotipriya Panda, 2025
