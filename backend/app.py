"""
KrishiVision AI — Primary Application Entry Point
=================================================
Exposes the complete production application integrating:
- Dual-Pathway Crop Recommendation (Path A with Random Forest ML + Path B Agro-Climatic Guidance)
- Deep Learning Foliar Plant Disease Diagnostics (MobileNetV2 Transfer Learning on PlantVillage)
- SQLite Relational Persistence (SQLAlchemy ORM with WAL mode)
- JWT Authentication & Farmer Profile Management
- Soil & Crop Historical Analytics
- Static UI Mounting & Interactive OpenAPI Swagger Documentation

Backward-compatible: can be run directly via:
    uvicorn backend.app:app --reload --port 8000
    uvicorn app.main:app --reload --app-dir backend --port 8000
    python backend/app.py
"""

import os
import sys
from pathlib import Path

# Add backend and project root directories to Python path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import full production FastAPI application
from app.main import app

# Re-export key schemas and inference functions for complete backward compatibility
from app.schemas.crop import SoilWeatherInput, CropGuidanceInput, PredictionResponse, GuidanceResponse
from app.ml.crop_recommendation.inference import predict_crop as predict_crop_model
from app.ml.crop_recommendation.guidance import get_crop_guidance
from app.ml.plant_disease.classifier import predict_leaf_disease

__all__ = [
    "app",
    "SoilWeatherInput",
    "CropGuidanceInput",
    "PredictionResponse",
    "GuidanceResponse",
    "predict_crop_model",
    "get_crop_guidance",
    "predict_leaf_disease",
]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
