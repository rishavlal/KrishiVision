"""
KrishiVision AI — Crop Recommendation Backend
=============================================
FastAPI service for crop recommendation using a trained
Random Forest machine learning model with soil and weather parameters.
"""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml.crop_recommendation.inference import predict_crop as predict_crop_model
from ml.crop_recommendation.guidance import get_crop_guidance


app = FastAPI(
    title="KrishiVision AI API",
    description="Crop recommendation service powered by a trained Random Forest model.",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SoilWeatherInput(BaseModel):
    """
    Input for the full ML-based crop recommendation path.

    These seven numerical fields are the actual features used by
    the trained Random Forest model.
    """

    # -------------------------
    # ML features
    # -------------------------
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

    # -------------------------
    # Application context
    # These are NOT ML features.
    # -------------------------
    location: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Farmer's location"
    )

    season: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Current agricultural season"
    )

    soil_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Known soil type"
    )

    water_availability: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Available water level"
    )

    irrigation_available: Optional[bool] = Field(
        default=None,
        description="Whether irrigation is available"
    )

    previous_crop: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Crop previously grown in the field"
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

                "location": "Jamshedpur",
                "season": "Kharif",
                "soil_type": "Loamy",
                "water_availability": "Moderate",
                "irrigation_available": True,
                "previous_crop": "Rice",
            }
        }


class CropGuidanceInput(BaseModel):
    location: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Farmer's state/location"
    )

    season: str = Field(
        ...,
        description="Growing season such as Kharif, Rabi or Zaid"
    )

    previous_crop: Optional[str] = Field(
        default=None,
        max_length=100
    )

    irrigation_available: Optional[bool] = None

    water_availability: Optional[str] = Field(
        default=None,
        description="Low, Moderate or High"
    )

    soil_type: Optional[str] = Field(
        default=None,
        max_length=100
    )


class PredictionResponse(BaseModel):
    crop: str
    confidence: float
    description: str
    timestamp: str


class GuidanceResponse(BaseModel):
    status: str
    message: str
    missing_for_ml_prediction: list[str]
    provided_information: dict
    timestamp: str


class DiseaseDetectionResponse(BaseModel):
    disease: str
    confidence: float
    recommendation: str


# ---------------------------------------------------------------------------
# Crop recommendation model
# ---------------------------------------------------------------------------

def run_crop_model(x):
    """
    Send ONLY the seven trained ML features to the Random Forest.
    Application-context fields are deliberately excluded.
    """

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
        description=(
            "Recommendation generated using the trained "
            "Random Forest crop recommendation model."
        ),
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "KrishiVision AI API",
        "status": "online"
    }


# ---------------------------------------------------------------------------
# PATH A — Soil report available
# ---------------------------------------------------------------------------

@app.post("/api/predict", response_model=PredictionResponse)
def predict_crop(payload: SoilWeatherInput):
    """
    Full ML-based crop recommendation.

    Requires the seven features used by the trained Random Forest.
    """

    try:
        return run_crop_model(payload)

    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}"
        )


# ---------------------------------------------------------------------------
# PATH B — No soil report
# ---------------------------------------------------------------------------

@app.post("/api/crop-guidance")
def crop_guidance(payload: CropGuidanceInput):
    try:
        result = get_crop_guidance(
            location=payload.location,
            season=payload.season,
            previous_crop=payload.previous_crop,
            irrigation_available=payload.irrigation_available,
            water_availability=payload.water_availability,
            soil_type=payload.soil_type,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Crop guidance failed: {exc}"
        )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z"
    }