"""
Plant Disease Schemas for KrishiVision
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DiseaseTreatmentInfo(BaseModel):
    organic: str
    chemical: str
    cultural: str


class DiseaseDetailResponse(BaseModel):
    class_id: str
    plant_name: str
    disease_name: str
    pathogen_type: str
    severity: str
    is_healthy: bool
    symptoms: str
    treatments: DiseaseTreatmentInfo


class DiseaseClassSummary(BaseModel):
    class_id: str
    plant_name: str
    disease_name: str
    pathogen_type: str
    severity: str
    is_healthy: bool


class DiseasePredictionResponse(BaseModel):
    model_status: str
    model_loaded: bool
    filename: Optional[str] = None
    image_details: Optional[Dict[str, Any]] = None
    message: str
    prediction: Optional[str] = None
    confidence: Optional[float] = Field(
        default=None,
        description="Maximum neural model output score as a percentage; not an empirically calibrated probability.",
    )
    disease_info: Optional[Dict[str, Any]] = None
    supported_classes: Optional[List[Dict[str, Any]]] = None
    timestamp: str
    record_id: Optional[int] = None
    persisted: bool = Field(default=False, description="Whether the scan was saved to database")
    persistence_error: Optional[str] = Field(default=None, description="Details if database persistence failed")
