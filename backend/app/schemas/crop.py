"""
Crop Recommendation Schemas for KrishiVision
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SoilWeatherInput(BaseModel):
    """
    Path A Input - Soil Report Available.
    7 trained numerical features used by the Random Forest model.
    """
    nitrogen: float = Field(..., ge=0, le=140, description="Nitrogen (N) kg/ha (0-140)")
    phosphorus: float = Field(..., ge=5, le=145, description="Phosphorus (P) kg/ha (5-145)")
    potassium: float = Field(..., ge=5, le=205, description="Potassium (K) kg/ha (5-205)")
    temperature: float = Field(..., ge=8.0, le=50.0, description="Temperature °C (8-50)")
    humidity: float = Field(..., ge=10.0, le=100.0, description="Relative Humidity % (10-100)")
    ph: float = Field(..., ge=3.5, le=10.0, description="Soil pH (3.5-10.0)")
    rainfall: float = Field(..., ge=20.0, le=350.0, description="Rainfall mm (20-350)")

    # Optional application context
    location: Optional[str] = Field(default=None, max_length=100)
    season: Optional[str] = Field(default=None, max_length=50)
    soil_type: Optional[str] = Field(default=None, max_length=50)
    water_availability: Optional[str] = Field(default=None, max_length=50)
    irrigation_available: Optional[bool] = Field(default=None)
    previous_crop: Optional[str] = Field(default=None, max_length=100)


class CropGuidanceInput(BaseModel):
    """
    Path B Input - Soil Report NOT Available.
    Preliminary guided recommendation based on agro-climatic context.
    """
    location: str = Field(..., min_length=2, max_length=100, description="State or District name")
    season: str = Field(..., description="Agricultural season (Kharif, Rabi, Zaid)")
    previous_crop: Optional[str] = Field(default=None, max_length=100)
    irrigation_available: Optional[bool] = Field(default=None)
    water_availability: Optional[str] = Field(default=None, description="Low, Moderate, High")
    soil_type: Optional[str] = Field(default=None, max_length=100)


class AlternativeCrop(BaseModel):
    crop: str
    confidence: float = Field(
        ...,
        description="Predicted-class probability from the Random Forest model; not empirically calibrated.",
    )
    description: str


class PredictionResponse(BaseModel):
    crop: str
    confidence: float = Field(
        ...,
        description="Predicted-class probability from the Random Forest model; not empirically calibrated.",
    )
    description: str
    alternatives: List[AlternativeCrop] = []
    timestamp: str
    record_id: Optional[int] = None
    persisted: bool = Field(default=False, description="Whether the prediction was saved to database")
    persistence_error: Optional[str] = Field(default=None, description="Details if database persistence failed")


class GuidanceRecommendation(BaseModel):
    crop: str
    reason: str
    matching_factors: List[str] = []


class GuidanceResponse(BaseModel):
    status: str = "guided_recommendation"
    location: str
    region: Optional[str] = None
    season: str
    recommendations: List[GuidanceRecommendation]
    soil_test_required: bool = True
    message: str
    timestamp: str
    record_id: Optional[int] = None
    persisted: bool = Field(default=False, description="Whether the guidance record was saved to the database")
    persistence_error: Optional[str] = Field(default=None, description="Details if database persistence failed")
