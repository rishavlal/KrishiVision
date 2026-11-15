"""
KrishiVision Analytics API Routes
=================================
Aggregates real farm prediction data, soil averages, and crop distribution statistics.
Strictly dynamic: no artificial fallback counts.
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..core.security import get_optional_current_user
from ..db.database import get_db
from ..db.models import User, CropPredictionRecord, DiseasePredictionRecord
from ..schemas.analytics import AnalyticsSummaryResponse, SoilAverages, CropCount

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Compute agricultural analytics.
    If authenticated, scopes to the logged-in farmer's records.
    If unauthenticated (guest / public dashboard), returns aggregate system analytics.
    """
    if current_user:
        crop_query = db.query(CropPredictionRecord).filter(
            CropPredictionRecord.user_id == current_user.id
        )
        disease_query = db.query(DiseasePredictionRecord).filter(
            DiseasePredictionRecord.user_id == current_user.id
        )
    else:
        crop_query = db.query(CropPredictionRecord)
        disease_query = db.query(DiseasePredictionRecord)

    total_crops = crop_query.count()
    total_diseases = disease_query.count()
    total_predictions = total_crops + total_diseases

    # Calculate real soil averages in a single aggregated query
    soil_records = crop_query.filter(CropPredictionRecord.nitrogen.isnot(None))
    soil_count = soil_records.count()

    if soil_count > 0:
        agg = soil_records.with_entities(
            func.avg(CropPredictionRecord.nitrogen),
            func.avg(CropPredictionRecord.phosphorus),
            func.avg(CropPredictionRecord.potassium),
            func.avg(CropPredictionRecord.ph),
            func.avg(CropPredictionRecord.rainfall)
        ).first()

        avg_n = round(float(agg[0] or 0.0), 1) if agg else 0.0
        avg_p = round(float(agg[1] or 0.0), 1) if agg else 0.0
        avg_k = round(float(agg[2] or 0.0), 1) if agg else 0.0
        avg_ph = round(float(agg[3] or 0.0), 2) if agg else 0.0
        avg_rainfall = round(float(agg[4] or 0.0), 1) if agg else 0.0

        # Real Soil Health Index (0-100 score based on pH neutrality and balanced NPK)
        ph_score = max(0, 100 - abs(avg_ph - 6.8) * 25)
        npk_balance = min(100, (avg_n / 100 + avg_p / 50 + avg_k / 50) / 3 * 85)
        soil_health_index = round((ph_score * 0.4 + npk_balance * 0.6), 1)
    else:
        avg_n = avg_p = avg_k = avg_ph = avg_rainfall = 0.0
        soil_health_index = 0.0

    # Real Crop distribution
    dist_base = db.query(CropPredictionRecord.predicted_crop, func.count(CropPredictionRecord.id))
    if current_user:
        dist_base = dist_base.filter(CropPredictionRecord.user_id == current_user.id)
    crop_dist_query = (
        dist_base.group_by(CropPredictionRecord.predicted_crop)
        .order_by(desc(func.count(CropPredictionRecord.id)))
        .all()
    )

    crop_distribution = []
    if total_crops > 0:
        for crop_name, count in crop_dist_query:
            crop_distribution.append(
                CropCount(
                    crop=crop_name,
                    count=count,
                    percentage=round((count / total_crops) * 100, 1)
                )
            )

    # Real Recent activity
    recent_crops = crop_query.order_by(desc(CropPredictionRecord.created_at)).limit(5).all()
    recent_activity = [
        {
            "id": r.id,
            "title": f"Recommended: {r.predicted_crop}",
            "confidence": f"{r.confidence}%" if r.confidence else "Guidance",
            "date": r.created_at.strftime("%b %d, %H:%M")
        }
        for r in recent_crops
    ]

    # Report cached model readiness separately from the presence of weight files.
    from ..ml.crop_recommendation import inference as crop_inference
    from ..ml.plant_disease import classifier as disease_classifier

    crop_ready = crop_inference._MODEL is not None
    disease_ready = disease_classifier._LOADED_MODEL is not None
    crop_file_exists = crop_inference.MODEL_PATH.exists()
    disease_file_exists = disease_classifier.find_model_file() is not None

    if crop_ready and disease_ready:
        system_status = "All ML model inference caches are loaded"
    elif crop_file_exists and disease_file_exists:
        system_status = "Model files available; inference readiness pending"
    elif crop_file_exists or disease_file_exists:
        system_status = "Partially available; one or more model files are missing or not loaded"
    else:
        system_status = "Degraded (ML model files unavailable)"

    return AnalyticsSummaryResponse(
        total_predictions=total_predictions,
        total_crop_predictions=total_crops,
        total_disease_scans=total_diseases,
        average_soil_health_index=soil_health_index,
        system_status=system_status,
        crop_distribution=crop_distribution,
        soil_averages=SoilAverages(
            n=avg_n,
            p=avg_p,
            k=avg_k,
            ph=avg_ph,
            rainfall=avg_rainfall
        ),
        recent_activity=recent_activity
    )
