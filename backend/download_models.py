"""
Download the DNN face models (YuNet detector + SFace recogniser) into ../models/.

These ONNX files power accurate face recognition in api_server.py. They are
git-ignored (large binaries), so run this once after cloning:

    python backend/download_models.py

If the models are missing, api_server.py still starts but falls back to a much
less accurate Haar-cascade pipeline.
"""
import sys
import urllib.request
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# OpenCV Zoo, served via the Git-LFS media endpoint so we get the real binaries.
MODELS = {
    "face_detection_yunet_2023mar.onnx":
        "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/"
        "models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx":
        "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/"
        "models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
}


def main() -> int:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in MODELS.items():
        dest = MODELS_DIR / name
        if dest.exists() and dest.stat().st_size > 100_000:
            print(f"[ok] {name} already present ({dest.stat().st_size:,} bytes)")
            continue
        print(f"[..] downloading {name} ...")
        urllib.request.urlretrieve(url, dest)
        size = dest.stat().st_size
        if size < 100_000:
            print(f"[!!] {name} looks too small ({size} bytes) -- download may have failed")
            return 1
        print(f"[ok] {name} ({size:,} bytes)")
    print("All models ready in", MODELS_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
