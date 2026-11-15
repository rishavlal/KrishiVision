"""
Automated Unit Tests for Crop Recommendation (Path A & Path B)
"""

import pytest
from app.ml.crop_recommendation.inference import predict_crop
from app.ml.crop_recommendation.guidance import get_crop_guidance


def test_path_a_ml_crop_prediction_rice():
    """Test Path A Random Forest prediction for rice conditions."""
    result = predict_crop(
        nitrogen=80.0,
        phosphorus=40.0,
        potassium=40.0,
        temperature=25.0,
        humidity=80.0,
        ph=6.5,
        rainfall=200.0
    )
    assert "crop" in result
    assert result["crop"].lower() in ["rice", "jute"]
    assert 0 <= result["confidence"] <= 100
    assert len(result["description"]) > 10
    assert isinstance(result["alternatives"], list)


def test_path_a_ml_crop_prediction_maize():
    """Test Path A Random Forest prediction for maize conditions."""
    result = predict_crop(
        nitrogen=78.0,
        phosphorus=45.0,
        potassium=20.0,
        temperature=24.0,
        humidity=65.0,
        ph=6.2,
        rainfall=90.0
    )
    assert "crop" in result
    assert 0 <= result["confidence"] <= 100


def test_path_b_crop_guidance_kharif():
    """Test Path B preliminary guidance for Jharkhand Kharif."""
    result = get_crop_guidance(
        location="Jharkhand",
        season="Kharif",
        water_availability="Moderate",
        irrigation_available=True
    )
    assert result["location"] == "Jharkhand"
    assert result["season"] == "Kharif"
    assert result["soil_test_required"] is True
    assert len(result["recommendations"]) > 0

    crop_names = [r["crop"].lower() for r in result["recommendations"]]
    assert "rice" in crop_names or "maize" in crop_names or "pigeonpea" in crop_names or "millets" in crop_names


def test_path_b_crop_guidance_rabi():
    """Test Path B preliminary guidance for Bihar Rabi."""
    result = get_crop_guidance(
        location="Bihar",
        season="Rabi",
        water_availability="Low",
        irrigation_available=False
    )
    assert result["season"] == "Rabi"
    assert len(result["recommendations"]) > 0
    crop_names = [r["crop"].lower() for r in result["recommendations"]]
    assert "chickpea" in crop_names or "mustard" in crop_names or "wheat" in crop_names
