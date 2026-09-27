"""
KrishiVision AI — Crop Recommendation Backend
===============================================
FastAPI service for crop recommendation using a trained
Random Forest machine learning model with soil and weather parameters.

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
    description="Crop recommendation service powered by a trained Random Forest model.",
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
    # Validation ranges are based on the observed ranges
    # in the crop recommendation training dataset.
    nitrogen: float = Field(
        ..., ge=0, le=140,
        description="Nitrogen content (dataset range: 0–140)"
    )
    phosphorus: float = Field(
        ..., ge=5, le=145,
        description="Phosphorus content (dataset range: 5–145)"
    )
    potassium: float = Field(
        ..., ge=5, le=205,
        description="Potassium content (dataset range: 5–205)"
    )
    temperature: float = Field(
        ..., ge=8.83, le=43.68,
        description="Temperature in °C (dataset range: 8.83–43.68)"
    )
    humidity: float = Field(
        ..., ge=14.26, le=99.98,
        description="Relative humidity in % (dataset range: 14.26–99.98)"
    )
    ph: float = Field(
        ..., ge=3.50, le=9.94,
        description="Soil pH (dataset range: 3.50–9.94)"
    )
    rainfall: float = Field(
        ..., ge=20.21, le=298.56,
        description="Rainfall in mm (dataset range: 20.21–298.56)"
    )

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
# Crop recommendation model
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
