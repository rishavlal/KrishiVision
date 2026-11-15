"""
KrishiVision AI - Plant Disease Vision Classifier & Image Preprocessing Pipeline
=================================================================================
Validates, preprocesses foliar images (224x224 RGB), and runs deep learning inference
when trained weights are loaded. Strictly transparent when weights are not present.
"""

import io
import os
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

from .disease_catalog import DISEASE_CATALOG, get_disease_detail, get_all_classes


MODEL_DIR = Path(__file__).resolve().parent / "model"
SUPPORTED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
TARGET_IMAGE_SIZE = (224, 224)

# Global model cache
_LOADED_MODEL = None
_MODEL_TYPE = None


def find_model_file() -> Optional[Path]:
    """Search model directory for supported trained weight formats."""
    if not MODEL_DIR.exists():
        return None
    for ext in ["*.pth", "*.pt", "*.h5", "*.keras", "*.onnx"]:
        for file in MODEL_DIR.glob(ext):
            if file.is_file() and file.stat().st_size > 1000:
                return file
    return None


def validate_and_preprocess_image(file_bytes: bytes, filename: str = "") -> Image.Image:
    """
    Validate foliar image file size, integrity, and dimensions.
    Returns RGB PIL Image resized to standard 224x224.
    """
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(
            f"File size exceeds maximum allowable limit of 10 MB (received {len(file_bytes)/(1024*1024):.2f} MB)."
        )

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Verify image integrity
    except Exception as exc:
        raise ValueError(f"Uploaded file is not a valid image format: {exc}")

    # Re-open after verify() closes the stream
    image = Image.open(io.BytesIO(file_bytes))

    # Convert grayscale or RGBA to 3-channel RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize to neural architecture target dimensions (224x224)
    image = image.resize(TARGET_IMAGE_SIZE, Image.Resampling.BILINEAR)
    return image


def predict_leaf_disease(file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
    """
    Main disease detection inference pipeline.
    Validates, preprocesses, and executes inference if trained weights are available.
    """
    # Step 1: Preprocess image
    image = validate_and_preprocess_image(file_bytes, filename)
    img_width, img_height = image.size

    # Step 2: Check for trained weights file
    model_path = find_model_file()

    if model_path is None:
        # Strictly compliant with User Rule: No fake or fabricated predictions
        return {
            "model_status": "model_weights_not_found",
            "model_loaded": False,
            "filename": filename,
            "image_details": {
                "format": "RGB",
                "dimensions": f"{img_width}x{img_height}",
                "status": "Validated and preprocessed successfully (224x224 RGB tensor ready)"
            },
            "message": (
                "Notice: Trained disease neural network weights (e.g. 'mobilenet_v2.pth' or '.h5') "
                "were not found in 'backend/app/ml/plant_disease/model/'. To prevent fabricated diagnosis, "
                "the system does not generate random or simulated predictions. "
                "Please review the 27 supported disease classes below or consult the treatment encyclopedia."
            ),
            "prediction": None,
            "confidence": None,
            "disease_info": None,
            "supported_classes": get_all_classes()
        }

    # Step 3: If weights exist, attempt real inference
    try:
        # Load weights and execute forward pass when weights artifact is supplied
        # Supports TensorFlow/Keras or PyTorch export
        if model_path.suffix in [".h5", ".keras"]:
            try:
                import tensorflow as tf
                global _LOADED_MODEL
                if _LOADED_MODEL is None:
                    _LOADED_MODEL = tf.keras.models.load_model(str(model_path))
                
                # Preprocess tensor
                img_array = tf.keras.preprocessing.image.img_to_array(image)
                img_array = tf.expand_dims(img_array, 0)
                img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
                
                predictions = _LOADED_MODEL.predict(img_array)
                raw_preds = predictions[0]
                # Check if predictions are already softmax probabilities
                if hasattr(raw_preds, "numpy"):
                    raw_preds = raw_preds.numpy()
                import numpy as np
                if np.isclose(np.sum(raw_preds), 1.0, atol=0.05):
                    score = raw_preds
                else:
                    score = tf.nn.softmax(raw_preds).numpy()

                # Load saved class names or fallback to sorted catalog keys
                class_names_file = MODEL_DIR / "class_names.json"
                if class_names_file.exists():
                    import json
                    with open(class_names_file, "r", encoding="utf-8") as f:
                        all_classes = json.load(f)
                else:
                    all_classes = sorted(list(DISEASE_CATALOG.keys()))

                pred_idx = int(np.argmax(score))
                predicted_class = all_classes[pred_idx] if pred_idx < len(all_classes) else "Unknown"
                confidence = round(float(np.max(score)) * 100, 2)
                disease_info = get_disease_detail(predicted_class)
                
                return {
                    "model_status": "inferred_successfully",
                    "model_loaded": True,
                    "filename": filename,
                    "message": f"Diagnosis completed with {confidence}% confidence.",
                    "image_details": {
                        "dimensions": f"{img_width}x{img_height}",
                        "status": "Inference completed via MobileNetV2 architecture"
                    },
                    "prediction": disease_info["disease_name"] if disease_info else predicted_class,
                    "confidence": confidence,
                    "disease_info": disease_info,
                    "supported_classes": get_all_classes()
                }
            except Exception as ml_err:
                raise RuntimeError(f"Neural inference execution error: {ml_err}")

        raise RuntimeError(f"Model format '{model_path.suffix}' detected but inference runner requires configuration.")

    except Exception as exc:
        return {
            "model_status": "inference_error",
            "model_loaded": True,
            "filename": filename,
            "message": f"Foliar diagnostic inference notice: {exc}",
            "error_detail": str(exc),
            "image_details": {
                "dimensions": f"{img_width}x{img_height}",
                "status": "Preprocessed successfully"
            },
            "prediction": None,
            "confidence": None,
            "disease_info": None,
            "supported_classes": get_all_classes()
        }
