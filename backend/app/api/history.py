"""
KrishiVision Prediction History API Routes
==========================================
Unified history access and management for crop recommendations and disease scans.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..core.security import get_current_user, get_optional_current_user
from ..db.database import get_db
from ..db.models import User, CropPredictionRecord, DiseasePredictionRecord
from ..core.time import format_india_datetime, utc_isoformat

router = APIRouter(tags=["Prediction History"])


@router.get("/api/history")
def get_unified_history(
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch prediction history.
    If authenticated, returns the user's personal crop predictions and disease detections.
    If unauthenticated, returns recent guest / community predictions.
    """
    if current_user:
        crop_query = db.query(CropPredictionRecord).filter(
            CropPredictionRecord.user_id == current_user.id
        )
        disease_query = db.query(DiseasePredictionRecord).filter(
            DiseasePredictionRecord.user_id == current_user.id
        )
    else:
        # Show recent guest/public predictions
        crop_query = db.query(CropPredictionRecord).filter(
            CropPredictionRecord.user_id.is_(None)
        )
        disease_query = db.query(DiseasePredictionRecord).filter(
            DiseasePredictionRecord.user_id.is_(None)
        )

    crops = crop_query.order_by(desc(CropPredictionRecord.created_at)).limit(20).all()
    diseases = disease_query.order_by(desc(DiseasePredictionRecord.created_at)).limit(20).all()

    combined = []
    for c in crops:
        npk_str = f"{int(c.nitrogen or 0)}-{int(c.phosphorus or 0)}-{int(c.potassium or 0)}" if c.nitrogen is not None else "N/A"
        rainfall_str = f"{int(c.rainfall)} mm" if c.rainfall is not None else "N/A"
        combined.append({
            "id": c.id,
            "type": "crop",
            "path": c.recommendation_path,
            "title": f"Crop Recommendation: {c.predicted_crop}",
            "crop": c.predicted_crop,
            "confidence": c.confidence,
            "npk": npk_str,
            "rainfall": rainfall_str,
            "location": c.location or "General",
            "date": format_india_datetime(c.created_at),
            "timestamp": utc_isoformat(c.created_at)
        })

    for d in diseases:
        combined.append({
            "id": d.id,
            "type": "disease",
            "title": f"Disease Scan: {d.disease_name}",
            "plant": d.plant_name,
            "disease": d.disease_name,
            "confidence": d.confidence,
            "severity": d.severity,
            "filename": d.filename,
            "date": format_india_datetime(d.created_at),
            "timestamp": utc_isoformat(d.created_at)
        })

    # Sort combined by timestamp descending
    combined.sort(key=lambda x: x["timestamp"], reverse=True)
    return combined


@router.get("/api/crop/history")
def get_crop_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve history of crop recommendations."""
    query = db.query(CropPredictionRecord).filter(
        CropPredictionRecord.user_id == current_user.id
    )
    records = query.order_by(desc(CropPredictionRecord.created_at)).limit(50).all()
    return records


@router.get("/api/disease/history")
def get_disease_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve history of plant disease detections."""
    query = db.query(DiseasePredictionRecord).filter(
        DiseasePredictionRecord.user_id == current_user.id
    )
    records = query.order_by(desc(DiseasePredictionRecord.created_at)).limit(50).all()
    return records


@router.delete("/api/history/{record_id}")
def delete_history_record(
    record_id: int,
    record_type: str = "crop",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a prediction record owned by the authenticated user."""
    if record_type == "disease":
        record = db.query(DiseasePredictionRecord).filter(DiseasePredictionRecord.id == record_id).first()
    else:
        record = db.query(CropPredictionRecord).filter(CropPredictionRecord.id == record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record #{record_id} not found."
        )

    if record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record #{record_id} not found."
        )

    try:
        db.delete(record)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete record: {exc}"
        )

    return {"status": "success", "message": f"Record #{record_id} deleted successfully."}
