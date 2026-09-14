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
def run_crop_model(x: SoilWeatherInput) -> PredictionResponse:
    n, p, k = x.nitrogen, x.phosphorus, x.potassium
    t, h, ph, r = x.temperature, x.humidity, x.ph, x.rainfall

    if r > 200 and n > 80 and h > 70:
        crop, conf, desc = (
            "Rice", 96.0,
            "High rainfall combined with strong nitrogen levels and humidity "
            "creates ideal paddy-field conditions.",
        )
    elif h > 80 and r > 150 and t > 24:
        crop, conf, desc = (
            "Coconut", 94.5,
            "High humidity and consistent warm rainfall closely match "
            "coastal coconut-growing regions.",
        )
    elif 60 < r <= 150 and h > 75 and t > 24:
        crop, conf, desc = (
            "Banana", 91.0,
            "Warm temperatures with steady rainfall and humidity favour "
            "banana plantations.",
        )
    elif r < 100 and ph < 6.8 and 23 <= t <= 28:
        crop, conf, desc = (
            "Coffee", 93.0,
            "Moderate temperature and slightly acidic soil are classic "
            "conditions for Arabica/Robusta coffee.",
        )
    elif k > 55 and p > 55 and r < 90 and t > 22:
        crop, conf, desc = (
            "Cotton", 92.5,
            "High potassium and phosphorus with low rainfall suit cotton's "
            "deep-root, drought-tolerant growth.",
        )
    elif n > 55 and 80 <= r <= 160 and t > 24:
        crop, conf, desc = (
            "Maize", 90.0,
            "Balanced nitrogen with moderate rainfall and warmth are ideal "
            "for maize development.",
        )
    elif ph < 6.2 and r < 90 and 15 <= t <= 25:
        crop, conf, desc = (
            "Grapes", 88.5,
            "Cooler temperatures, low rainfall, and slightly acidic soil "
            "resemble vineyard conditions.",
        )
    elif t > 30 and h < 55 and r < 60:
        crop, conf, desc = (
            "Watermelon", 87.0,
            "Hot, dry conditions with low rainfall are well suited to "
            "melon crops.",
        )
    elif ph >= 6.5 and r < 80 and 20 <= t <= 30 and h < 60:
        crop, conf, desc = (
            "Pomegranate", 89.0,
            "Warm, arid conditions with moderate soil pH suit drought-hardy "
            "pomegranate orchards.",
        )
    elif r > 150 and h > 70 and t > 22:
        crop, conf, desc = (
            "Jute", 86.0,
            "High rainfall and humidity are typical of jute-growing "
            "floodplain regions.",
        )
    elif n < 40 and p > 40 and r < 100:
        crop, conf, desc = (
            "Chickpea", 85.5,
            "Lower nitrogen requirement and modest rainfall favour "
            "nitrogen-fixing chickpea.",
        )
    elif n < 45 and k < 40 and r < 90:
        crop, conf, desc = (
            "Lentil", 84.0,
            "Low nitrogen and potassium demand with limited rainfall suit "
            "lentil cultivation.",
        )
    elif 18 <= t <= 24 and h < 65 and r < 100:
        crop, conf, desc = (
            "Apple", 90.5,
            "Cool temperatures and lower humidity match temperate orchard "
            "conditions for apples.",
        )
    else:
        crop, conf, desc = (
            "Mixed Legumes", 78.0,
            "Conditions are moderate across all parameters; a legume "
            "rotation is a safe, soil-restoring choice.",
        )

    return PredictionResponse(
        crop=crop,
        confidence=conf,
        description=desc,
        timestamp=datetime.utcnow().isoformat() + "Z",
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
