"""
KrishiVision AI - Crop Recommendation Inference Engine
======================================================
Loads the trained Random Forest classifier and executes inference across 22 crops.
Provides top recommended crop, predicted-class probability scores, and top alternatives.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
import joblib
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "crop_model.pkl"

FEATURES = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
]

# Agronomic descriptions for crops
CROP_EXPLANATIONS = {
    "rice": "High water and humidity tolerance with balanced nitrogen ensures high paddy yield.",
    "maize": "Well-drained soil with warm temperature and moderate rainfall is ideal for maize growth.",
    "chickpea": "Requires cool, dry climate and low moisture; well suited for post-monsoon rabi soils.",
    "kidneybeans": "Thrives in mild temperatures and fertile, well-aerated loam with moderate precipitation.",
    "pigeonpeas": "Drought-tolerant legume well-adapted to semi-arid tropical soils and low rainfall.",
    "mothbeans": "Highly drought-resistant legume ideal for arid tracts with sandy loam and low rainfall.",
    "mungbean": "Short-duration crop suited for warm weather, moderate humidity, and quick moisture turnaround.",
    "blackgram": "Suited for hot and humid climates; enriches soil fertility via nitrogen fixation.",
    "lentil": "Cold-tolerant rabi legume performing best in light loams under low to moderate rainfall.",
    "pomegranate": "Thrives in dry, warm climates with low rainfall and alkaline to neutral soils.",
    "banana": "Demands high moisture, warmth, and rich potassium availability throughout its growth cycle.",
    "mango": "Performs well in frost-free tropical and subtropical climates with distinct dry and wet periods.",
    "grapes": "Requires warm, dry summers and slightly acidic, well-drained gravelly or sandy loam.",
    "watermelon": "Warm temperature and low humidity with abundant sunshine ensure sweet fruit development.",
    "muskmelon": "Prefers hot, dry atmosphere and sandy loam soils with moderate potassium and phosphorus.",
    "apple": "Temperate fruit crop needing adequate winter chilling hours and well-aerated fertile soils.",
    "orange": "Subtropical citrus needing moderate rainfall, good soil drainage, and adequate nitrogen.",
    "papaya": "Continuous warmth, high humidity, and frost-free conditions with rich organic drainage.",
    "coconut": "Thrives in humid tropical coastal zones with consistent rainfall and warm sunshine.",
    "cotton": "Requires warm climate, ample sunshine, high potassium, and low rainfall during ripening.",
    "jute": "Warm, humid tropical climate with abundant monsoon rainfall is optimal for fibrous vegetative growth.",
    "coffee": "Grows best in humid, tropical upland shade with rich acidic soil and steady moderate rainfall."
}

# Cache loaded model
_MODEL = None


def get_model():
    """Load model with thread-safe singleton cache."""
    global _MODEL
    if _MODEL is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained Random Forest model file not found at: {MODEL_PATH}"
            )
        _MODEL = joblib.load(MODEL_PATH)
    return _MODEL


def predict_crop(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float
) -> Dict[str, Any]:
    """
    Execute crop recommendation inference using the trained Random Forest model.

    Returns:
        Dictionary containing:
        - crop: Primary recommended crop name
        - confidence: Predicted-class probability percentage (0-100); not empirically calibrated
        - description: Agronomic reason for the recommendation
        - alternatives: Top 3 alternative crops with respective probabilities
    """
    model = get_model()

    input_df = pd.DataFrame([{
        "N": float(nitrogen),
        "P": float(phosphorus),
        "K": float(potassium),
        "temperature": float(temperature),
        "humidity": float(humidity),
        "ph": float(ph),
        "rainfall": float(rainfall)
    }])[FEATURES]

    # Predict class
    prediction = model.predict(input_df)[0]

    # Predict probabilities across all classes
    probabilities = model.predict_proba(input_df)[0]
    classes = model.classes_

    # Primary confidence
    max_idx = np.argmax(probabilities)
    confidence = round(float(probabilities[max_idx]) * 100, 2)

    # Sort top alternatives
    sorted_indices = np.argsort(probabilities)[::-1]
    alternatives = []
    for idx in sorted_indices[1:4]:  # Next top 3
        alt_crop = str(classes[idx])
        alt_prob = round(float(probabilities[idx]) * 100, 2)
        if alt_prob > 0.5:
            alternatives.append({
                "crop": alt_crop.capitalize(),
                "confidence": alt_prob,
                "description": CROP_EXPLANATIONS.get(alt_crop.lower(), "Suitable secondary alternative.")
            })

    pred_clean = str(prediction).capitalize()
    explanation = CROP_EXPLANATIONS.get(
        str(prediction).lower(),
        f"This crop is well-suited for your field's N-P-K ({nitrogen}-{phosphorus}-{potassium}) and rainfall ({rainfall}mm) profile."
    )

    return {
        "crop": pred_clean,
        "confidence": confidence,
        "description": explanation,
        "alternatives": alternatives
    }
