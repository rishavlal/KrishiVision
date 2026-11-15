"""
Analytics Schemas for KrishiVision
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class SoilAverages(BaseModel):
    n: float
    p: float
    k: float
    ph: float
    rainfall: float


class CropCount(BaseModel):
    crop: str
    count: int
    percentage: float


class AnalyticsSummaryResponse(BaseModel):
    total_predictions: int
    total_crop_predictions: int
    total_disease_scans: int
    average_soil_health_index: float
    system_status: str
    crop_distribution: List[CropCount]
    soil_averages: SoilAverages
    recent_activity: List[Dict[str, Any]]
