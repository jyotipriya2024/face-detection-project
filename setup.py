"""
Setup script for Optimized Machine Learning Model for Accurate Face Detection in Real-Time Application
Installs dependencies and initializes the project
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a shell command and report status."""
    print(f"\n{'=' * 60}")
    print(f"▶ {description}")
    print(f"{'=' * 60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✓ {description} completed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description} failed")
        print(f"Error code: {e.returncode}\n")
        return False


def main():
    """Main setup function."""
    print("\n" + "=" * 60)
    print("Face Detection System - Setup Script")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✓ Python version: {sys.version}")
    
    # Create necessary directories
    print("\n▶ Creating project directories...")
    directories = ['data', 'models', 'output', 'logs', 'sample_images', 'batch_input', 'batch_output', 'face_database']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✓ Created: {directory}/")
    
    # Upgrade pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠ Warning: pip upgrade failed, continuing anyway...")
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing dependencies"):
        print("✗ Failed to install dependencies")
        sys.exit(1)
    
    # Verify installations
    print("\n▶ Verifying installations...")
    try:
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")
    except ImportError:
        print("✗ OpenCV not found")
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow: {tf.__version__}")
    except ImportError:
        print("✗ TensorFlow not found")
    
    try:
        import mediapipe as mp
        print(f"✓ MediaPipe: {mp.__version__}")
    except ImportError:
        print("✗ MediaPipe not found")
    
    try:
        import numpy as np
        print(f"✓ NumPy: {np.__version__}")
    except ImportError:
        print("✗ NumPy not found")
    
    # Setup complete
    print("\n" + "=" * 60)
    print("✓ Setup completed successfully!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  1. Run: python main.py")
    print("  2. Or try examples: python examples.py")
    print("  3. Read README.md for detailed documentation")
    
    print("\nQuick start:")
    print("  - Real-time detection: python main.py")
    print("  - Run examples: python examples.py")


if __name__ == "__main__":
    main()
