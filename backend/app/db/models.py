"""
KrishiVision Database Models
=============================
Relational schemas for Farmer accounts, Crop prediction records,
and Plant disease inspection history.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from .database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    farm_location = Column(String(100), default="Jharkhand, India")
    farm_size_hectares = Column(Float, default=2.5)
    phone_number = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    # Relationships
    crop_predictions = relationship("CropPredictionRecord", back_populates="user", cascade="all, delete-orphan")
    disease_predictions = relationship("DiseasePredictionRecord", back_populates="user", cascade="all, delete-orphan")


class RevokedAccessToken(Base):
    __tablename__ = "revoked_access_tokens"

    token_hash = Column(String(64), primary_key=True)
    expires_at = Column(Float, nullable=False)


class UserTokenInvalidation(Base):
    __tablename__ = "user_token_invalidations"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    invalid_before = Column(Float, nullable=False)


class CropPredictionRecord(Base):
    __tablename__ = "crop_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Path classification
    recommendation_path = Column(String(30), default="ml_soil_report")  # 'ml_soil_report' or 'guided_no_soil'

    # Soil & Weather Parameters (Optional for Path B)
    nitrogen = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)

    # Contextual parameters
    location = Column(String(100), nullable=True)
    season = Column(String(50), nullable=True)
    soil_type = Column(String(50), nullable=True)

    # Result
    predicted_crop = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="crop_predictions")


class DiseasePredictionRecord(Base):
    __tablename__ = "disease_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    filename = Column(String(255), nullable=True)
    plant_name = Column(String(100), nullable=False)
    disease_name = Column(String(150), nullable=False)
    predicted_class = Column(String(150), nullable=False)
    confidence = Column(Float, nullable=True)
    severity = Column(String(50), default="Moderate")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=get_utc_now)

    user = relationship("User", back_populates="disease_predictions")
