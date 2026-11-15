"""
KrishiVision Crop Recommendation API Routes
============================================
Supports both agricultural pathways:
- PATH A: Soil Report Available (Trained Random Forest ML Model)
- PATH B: Soil Report Not Available (Preliminary Agro-Climatic Rule Engine)
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import get_optional_current_user
from ..db.database import get_db
from ..db.models import User, CropPredictionRecord
from ..schemas.crop import (
    SoilWeatherInput,
    CropGuidanceInput,
    PredictionResponse,
    GuidanceResponse,
    AlternativeCrop
)
from ..ml.crop_recommendation.inference import predict_crop as run_crop_model
from ..ml.crop_recommendation.guidance import get_crop_guidance

router = APIRouter(tags=["Crop Recommendation"])


# ---------------------------------------------------------------------------
# PATH A — Soil Report Available (Full ML Random Forest Prediction)
# ---------------------------------------------------------------------------

@router.post("/api/predict", response_model=PredictionResponse)
@router.post("/api/crop/predict", response_model=PredictionResponse)
def predict_crop(
    payload: SoilWeatherInput,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    PATH A: Full ML-based crop recommendation using trained Random Forest model.
    Accepts 7 soil and meteorological features:
    Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, Soil pH, Rainfall.
    """
    try:
        result = run_crop_model(
            nitrogen=payload.nitrogen,
            phosphorus=payload.phosphorus,
            potassium=payload.potassium,
            temperature=payload.temperature,
            humidity=payload.humidity,
            ph=payload.ph,
            rainfall=payload.rainfall
        )

        # Persist prediction record in database
        persisted = False
        persistence_error = None
        saved_id = None
        try:
            record = CropPredictionRecord(
                user_id=current_user.id if current_user else None,
                recommendation_path="ml_soil_report",
                nitrogen=payload.nitrogen,
                phosphorus=payload.phosphorus,
                potassium=payload.potassium,
                temperature=payload.temperature,
                humidity=payload.humidity,
                ph=payload.ph,
                rainfall=payload.rainfall,
                location=payload.location,
                season=payload.season,
                soil_type=payload.soil_type,
                predicted_crop=result["crop"],
                confidence=result["confidence"],
                description=result["description"]
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            saved_id = record.id
            persisted = True
        except Exception as db_exc:
            db.rollback()
            saved_id = None
            persisted = False
            persistence_error = f"Database persistence failed: {db_exc}"

        return PredictionResponse(
            crop=result["crop"],
            confidence=result["confidence"],
            description=result["description"],
            alternatives=[AlternativeCrop(**alt) for alt in result.get("alternatives", [])],
            timestamp=datetime.now(timezone.utc).isoformat(),
            record_id=saved_id,
            persisted=persisted,
            persistence_error=persistence_error
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crop prediction failed: {exc}"
        )


# ---------------------------------------------------------------------------
# PATH B — Soil Report NOT Available (Preliminary Guidance Engine)
# ---------------------------------------------------------------------------

@router.post("/api/crop-guidance", response_model=GuidanceResponse)
@router.post("/api/crop/guidance", response_model=GuidanceResponse)
def crop_guidance(
    payload: CropGuidanceInput,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    PATH B: Preliminary rule-based crop guidance when laboratory soil report is unavailable.
    Collects agro-climatic context: State/Location, Season, Previous Crop, Irrigation, Soil Type.
    Distinguished clearly from ML inference; encourages official soil testing.
    """
    try:
        result = get_crop_guidance(
            location=payload.location,
            season=payload.season,
            previous_crop=payload.previous_crop,
            irrigation_available=payload.irrigation_available,
            water_availability=payload.water_availability,
            soil_type=payload.soil_type
        )

        top_crop = result["recommendations"][0]["crop"] if result.get("recommendations") else "General Legumes"

        # Persist guidance record safely
        persisted = False
        persistence_error = None
        saved_id = None
        try:
            record = CropPredictionRecord(
                user_id=current_user.id if current_user else None,
                recommendation_path="guided_no_soil",
                location=payload.location,
                season=payload.season,
                soil_type=payload.soil_type,
                predicted_crop=top_crop,
                confidence=None,
                description=result["message"]
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            saved_id = record.id
            persisted = True
        except Exception as db_exc:
            db.rollback()
            persistence_error = f"Database persistence failed: {db_exc}"

        return GuidanceResponse(
            status="guided_recommendation",
            location=result["location"],
            region=result.get("region"),
            season=result["season"],
            recommendations=result["recommendations"],
            soil_test_required=True,
            message=result["message"],
            timestamp=datetime.now(timezone.utc).isoformat(),
            record_id=saved_id,
            persisted=persisted,
            persistence_error=persistence_error
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crop guidance generation failed: {exc}"
        )
