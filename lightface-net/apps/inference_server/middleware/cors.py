# apps/inference_server/middleware/cors.py
"""CORS middleware configuration for the inference server."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def add_cors_middleware(app: FastAPI,
                        allow_origins: list[str] | None = None) -> None:
    """
    Attach CORSMiddleware.  Default to localhost origins for demo safety.
    Override allow_origins in production.
    """
    origins = allow_origins or [
        "http://localhost",
        "http://localhost:8501",   # Streamlit demo
        "http://localhost:3000",   # React front-end (if any)
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
