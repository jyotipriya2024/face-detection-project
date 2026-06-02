# apps/inference_server/main.py
"""
LightFace-Net FastAPI Inference Server.

Endpoints:
  POST /detect   — Detect faces in an uploaded image
  GET  /health   — Health check
  GET  /metrics  — Current FPS / latency / memory stats

Start:
    uvicorn apps.inference_server.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations
import io
import logging
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from features.detection.pipeline import DetectionPipeline
from apps.inference_server.middleware.cors import add_cors_middleware
from apps.inference_server.middleware.rate_limiter import RateLimitMiddleware

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="LightFace-Net Inference API",
    description=(
        "Real-time face detection API — "
        "Jyotipriya Panda | MTech CSE | GIFT Bhubaneswar 2024-26"
    ),
    version="1.0.0",
)

add_cors_middleware(app)
app.add_middleware(RateLimitMiddleware)

# ---------------------------------------------------------------------------
# Model loading (lazy singleton)
# ---------------------------------------------------------------------------

_pipeline: DetectionPipeline | None = None
_CONFIG_PATH = Path('infrastructure/config/model_config.yaml')


def _get_pipeline() -> DetectionPipeline:
    global _pipeline
    if _pipeline is None:
        if _CONFIG_PATH.exists():
            _pipeline = DetectionPipeline.from_config(str(_CONFIG_PATH))
        else:
            _pipeline = DetectionPipeline()
        logger.info("DetectionPipeline loaded.")
    return _pipeline


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get('/health')
async def health_check() -> dict:
    """Liveness probe — returns 200 when the server is ready."""
    pipeline = _get_pipeline()
    return {
        'status': 'ok',
        'model': 'LightFace-Net',
        'device': str(pipeline.device),
    }


@app.post('/detect')
async def detect_faces(image: UploadFile = File(...)) -> JSONResponse:
    """
    Detect faces in an uploaded image.

    Accepts: JPEG / PNG (max 2 MB).
    Returns: JSON with detected face bounding boxes and confidence scores.
    """
    # Validate content type
    if image.content_type not in ('image/jpeg', 'image/png', 'image/jpg'):
        raise HTTPException(
            status_code=415,
            detail="Unsupported media type. Upload JPEG or PNG."
        )

    raw = await image.read()
    if len(raw) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 2 MB).")

    # Decode
    arr = np.frombuffer(raw, dtype=np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        raise HTTPException(status_code=422, detail="Could not decode image.")

    pipeline = _get_pipeline()
    detections = pipeline.detect(bgr)

    return JSONResponse({
        'faces': [d.to_dict() for d in detections],
        'count': len(detections),
        'fps': pipeline.last_fps,
    })


@app.get('/metrics')
async def get_metrics() -> dict:
    """Returns current inference performance metrics."""
    return _get_pipeline().get_performance_metrics()
