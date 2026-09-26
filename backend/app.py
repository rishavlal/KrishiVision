"""
KrishiVision AI — Crop Recommendation Backend
===============================================
Production-style FastAPI service that simulates an ML-driven crop
recommendation engine using rule-based logic over soil (N-P-K, pH) and
weather (temperature, humidity, rainfall) parameters.

Run locally:
    pip install fastapi uvicorn pydantic
    uvicorn app:app --reload --port 8000

The frontend (index.html) calls POST http://localhost:8000/api/predict
"""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from ml.crop_recommendation.inference import predict_crop as predict_crop_model

app = FastAPI(
    title="KrishiVision AI API",
    description="Rule-based crop recommendation and disease-detection service",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the static/HTML frontend (served from any origin during local
# development) to call this API via fetch().
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten this to your deployed frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class SoilWeatherInput(BaseModel):
    nitrogen: float = Field(..., ge=0, le=300, description="Nitrogen content (kg/ha)")
    phosphorus: float = Field(..., ge=0, le=200, description="Phosphorus content (kg/ha)")
    potassium: float = Field(..., ge=0, le=250, description="Potassium content (kg/ha)")
    temperature: float = Field(..., ge=-10, le=55, description="Ambient temperature (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    ph: float = Field(..., ge=0, le=14, description="Soil pH")
    rainfall: float = Field(..., ge=0, le=1000, description="Rainfall (mm)")

    class Config:
        json_schema_extra = {
            "example": {
                "nitrogen": 90,
                "phosphorus": 42,
                "potassium": 43,
                "temperature": 28.5,
                "humidity": 72,
                "ph": 6.5,
                "rainfall": 202,
            }
        }


class PredictionResponse(BaseModel):
    crop: str
    confidence: float
    description: str
    timestamp: str


class DiseaseDetectionResponse(BaseModel):
    disease: str
    confidence: float
    recommendation: str


# ---------------------------------------------------------------------------
# Core "model" — a transparent, rule-based simulation of a trained classifier.
# Rules are ordered from most to least specific; the first matching rule wins.
# ---------------------------------------------------------------------------
def run_crop_model(x):
    result = predict_crop_model(
        nitrogen=x.nitrogen,
        phosphorus=x.phosphorus,
        potassium=x.potassium,
        temperature=x.temperature,
        humidity=x.humidity,
        ph=x.ph,
        rainfall=x.rainfall
    )

    return PredictionResponse(
        crop=result["crop"],
        confidence=result["confidence"],
        description="Recommendation generated using the trained Random Forest crop recommendation model.",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"service": "KrishiVision AI API", "status": "online"}


@app.post("/api/predict", response_model=PredictionResponse)
def predict_crop(payload: SoilWeatherInput):
    try:
        return run_crop_model(payload)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}
