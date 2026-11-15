"""
KrishiVision Plant Disease Detection API Routes
================================================
Handles leaf image upload, validation, preprocessing, and disease identification.
Provides complete 27-class diagnostic encyclopedia with symptoms, organic, chemical,
and cultural treatment regimens.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from sqlalchemy.orm import Session

from ..core.security import get_optional_current_user
from ..db.database import get_db
from ..db.models import User, DiseasePredictionRecord
from ..schemas.disease import (
    DiseaseClassSummary,
    DiseaseDetailResponse,
    DiseasePredictionResponse
)
from ..ml.plant_disease.classifier import predict_leaf_disease
from ..ml.plant_disease.disease_catalog import get_all_classes, get_disease_detail

logger = logging.getLogger("krishivision.disease")

router = APIRouter(prefix="/api/disease", tags=["Plant Disease Detection"])

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
CHUNK_SIZE = 64 * 1024  # 64 KB


@router.get("/classes", response_model=List[DiseaseClassSummary])
def list_disease_classes():
    """Retrieve full catalog of 27 supported plant disease conditions across 6 species."""
    return get_all_classes()


@router.get("/classes/{class_id}", response_model=DiseaseDetailResponse)
def get_disease_information(class_id: str):
    """Retrieve comprehensive agronomic information, symptoms, and 3-tier treatments."""
    detail = get_disease_detail(class_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant disease class '{class_id}' not found in catalog."
        )
    return detail


@router.post("/predict", response_model=DiseasePredictionResponse)
async def detect_leaf_disease(
    request: Request,
    file: UploadFile = File(..., description="Uploaded leaf photograph (JPG, PNG, WEBP)"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and evaluate crop leaf photograph.
    Validates upload size (<= 10MB) before full memory load, image dimensions, and format.
    Runs MobileNetV2 neural classifier. Returns explicit persistence and error status.
    """
    # E-07: Fast reject via Content-Length header if present
    content_length_header = request.headers.get("content-length")
    if content_length_header:
        try:
            cl = int(content_length_header)
            if cl > MAX_UPLOAD_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Upload payload size ({cl} bytes) exceeds the maximum allowed 10 MB limit."
                )
        except ValueError:
            pass

    # Stream read with size threshold enforcement to prevent memory exhaustion
    total_bytes = bytearray()
    try:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            total_bytes.extend(chunk)
            if len(total_bytes) > MAX_UPLOAD_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Uploaded image exceeds the maximum allowed 10 MB limit."
                )
    except HTTPException:
        raise
    except Exception as read_exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read upload stream: {read_exc}"
        )

    if len(total_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty. Please upload a valid image of a plant leaf."
        )

    file_bytes = bytes(total_bytes)
    filename = file.filename or "uploaded_leaf.jpg"

    # E-01: Run leaf disease classifier, raising explicit HTTP errors on model or format failure
    try:
        result = predict_leaf_disease(file_bytes, filename)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except FileNotFoundError as fnf_err:
        logger.error(f"Disease detection model file not found: {fnf_err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Disease detection model is not available: {fnf_err}"
        )
    except RuntimeError as rt_err:
        logger.error(f"Disease detection inference error: {rt_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disease detection inference failed: {rt_err}"
        )
    except Exception as exc:
        logger.error(f"Unexpected disease detection error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plant disease detection failed: {exc}"
        )

    # E-02: Only persist successful predictions to database; track persistence status explicitly
    saved_id = None
    persisted = False
    persistence_error = None

    try:
        record = DiseasePredictionRecord(
            user_id=current_user.id if current_user else None,
            filename=filename,
            plant_name=result.get("disease_info", {}).get("plant_name", "Crop Leaf") if result.get("disease_info") else "Crop Leaf Scan",
            disease_name=result.get("prediction") or "Inspection Logged",
            predicted_class=result.get("prediction") or "Unknown_Class",
            confidence=result.get("confidence"),
            severity=result.get("disease_info", {}).get("severity", "Info") if result.get("disease_info") else "Info",
            notes=result.get("message", "Foliar diagnostic complete.")
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        saved_id = record.id
        persisted = True
    except Exception as db_exc:
        db.rollback()
        persisted = False
        persistence_error = f"Database persistence failed: {db_exc}"
        logger.warning(f"Could not persist disease prediction to database: {db_exc}")

    return DiseasePredictionResponse(
        model_status=result.get("model_status", "operational"),
        model_loaded=result.get("model_loaded", True),
        filename=filename,
        image_details=result.get("image_details"),
        message=result.get("message", "Foliar diagnostic complete."),
        prediction=result.get("prediction"),
        confidence=result.get("confidence"),
        disease_info=result.get("disease_info"),
        supported_classes=result.get("supported_classes"),
        timestamp=datetime.now(timezone.utc).isoformat(),
        record_id=saved_id,
        persisted=persisted,
        persistence_error=persistence_error
    )
