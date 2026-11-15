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
import numpy as np

from .disease_catalog import DISEASE_CATALOG, get_disease_detail, get_all_classes


MODEL_DIR = Path(__file__).resolve().parent / "model"
SUPPORTED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
TARGET_IMAGE_SIZE = (224, 224)
MAX_IMAGE_DIMENSION = 5000
MIN_IMAGE_DIMENSION = 10
SUPPORTED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}

# Set PIL decompression bomb limit
Image.MAX_IMAGE_PIXELS = 25_000_000

# Global model cache
_LOADED_MODEL = None
_MODEL_TYPE = None


def find_model_file() -> Optional[Path]:
    """Search model directory for supported trained weight formats."""
    if not MODEL_DIR.exists():
        return None
    for ext in ["*.keras", "*.h5", "*.pth", "*.pt", "*.onnx"]:
        for file in MODEL_DIR.glob(ext):
            if file.is_file() and file.stat().st_size > 1000:
                return file
    return None


def validate_and_preprocess_image(file_bytes: bytes, filename: str = "") -> Image.Image:
    """
    Validate foliar image file size, integrity, format, and dimensions.
    Returns RGB PIL Image resized to standard 224x224.
    """
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(
            f"File size exceeds maximum allowable limit of 10 MB (received {len(file_bytes)/(1024*1024):.2f} MB)."
        )

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image_format = (image.format or "").upper()
        if image_format not in SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"Unsupported image format: {image_format or 'unknown'}. Supported formats: JPEG, PNG, WEBP.")
        image.verify()  # Verify image integrity
    except Exception as exc:
        raise ValueError(f"Uploaded file is not a valid image format: {exc}")

    # Re-open after verify() closes the stream
    image = Image.open(io.BytesIO(file_bytes))

    # Enforce dimension limits to prevent memory exhaustion and decompression bombs
    if image.width > MAX_IMAGE_DIMENSION or image.height > MAX_IMAGE_DIMENSION:
        raise ValueError(
            f"Image dimensions ({image.width}x{image.height}) exceed maximum allowed dimensions of {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION} pixels."
        )
    if image.width < MIN_IMAGE_DIMENSION or image.height < MIN_IMAGE_DIMENSION:
        raise ValueError(
            f"Image dimensions ({image.width}x{image.height}) are too small for foliar analysis (minimum {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION} pixels)."
        )

    # Convert grayscale or RGBA to 3-channel RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize to neural architecture target dimensions (224x224)
    image = image.resize(TARGET_IMAGE_SIZE, Image.Resampling.BILINEAR)
    return image


def _assess_plant_image(image: Image.Image) -> Optional[str]:
    """Reject clear non-foliage images and withhold uncertain images from the disease model."""
    sample = image.resize((96, 96), Image.Resampling.BILINEAR)
    rgb = np.asarray(sample, dtype=np.uint8)
    red, green, blue = (rgb[:, :, channel].astype(np.float32) for channel in range(3))

    vegetation_ratio = float(
        ((green > red * 1.08) & (green > blue * 0.95) & (green > 40)).mean()
    )
    ycbcr = np.asarray(sample.convert("YCbCr"), dtype=np.uint8)
    luminance, chroma_blue, chroma_red = (
        ycbcr[:, :, channel] for channel in range(3)
    )
    skin_ratio = float(
        (
            (chroma_blue >= 77)
            & (chroma_blue <= 127)
            & (chroma_red >= 133)
            & (chroma_red <= 173)
            & (luminance > 60)
        ).mean()
    )
    hsv = np.asarray(sample.convert("HSV"), dtype=np.uint8)
    mean_saturation = float(hsv[:, :, 1].mean() / 255)
    bright_background_ratio = float(
        ((red > 220) & (green > 220) & (blue > 220)).mean()
    )
    brightness_std = float(np.std(rgb.mean(axis=2)))

    invalid_message = "Invalid Image — Please upload a clear crop leaf photograph."
    if skin_ratio >= 0.22:
        raise ValueError(invalid_message)
    if (
        bright_background_ratio >= 0.55
        and mean_saturation < 0.12
        and vegetation_ratio < 0.05
    ):
        raise ValueError(invalid_message)

    if vegetation_ratio < 0.025 or brightness_std < 8:
        return (
            "Uncertain Image — Please upload a clear crop leaf photograph "
            "with visible foliage."
        )
    return None


def predict_leaf_disease(file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
    """
    Main disease detection inference pipeline.
    Validates, preprocesses, and executes inference if trained weights are available.
    """
    # Step 1: Preprocess image
    image = validate_and_preprocess_image(file_bytes, filename)
    img_width, img_height = image.size
    image_uncertainty = _assess_plant_image(image)
    if image_uncertainty:
        return {
            "model_status": "uncertain_image",
            "model_loaded": False,
            "filename": filename,
            "message": image_uncertainty,
            "prediction": None,
            "confidence": None,
            "disease_info": None,
            "image_details": {
                "dimensions": f"{img_width}x{img_height}",
                "status": "Insufficient visual evidence of crop foliage"
            },
            "supported_classes": get_all_classes()
        }

    # Step 2: Check for trained weights file
    model_path = find_model_file()

    if model_path is None:
        raise FileNotFoundError(
            "Trained disease neural network weights were not found in 'backend/app/ml/plant_disease/model/'. "
            "Please ensure 'plant_disease_model.keras' is present."
        )

    # Step 3: Attempt real inference
    try:
        if model_path.suffix in [".h5", ".keras"]:
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
            if hasattr(raw_preds, "numpy"):
                raw_preds = raw_preds.numpy()
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

            sorted_indices = np.argsort(score)[::-1]
            pred_idx = int(sorted_indices[0])
            confidence_score = float(score[pred_idx])
            second_score = float(score[sorted_indices[1]]) if len(sorted_indices) > 1 else 0.0
            confidence = round(confidence_score * 100, 2)
            if confidence_score < 0.45 or confidence_score - second_score < 0.10:
                return {
                    "model_status": "uncertain_prediction",
                    "model_loaded": True,
                    "filename": filename,
                    "message": (
                        "The image could not be matched to a disease with enough "
                        "certainty. Please upload a clear crop leaf photograph."
                    ),
                    "prediction": None,
                    "confidence": None,
                    "disease_info": None,
                    "image_details": {
                        "dimensions": f"{img_width}x{img_height}",
                        "status": "Model output was not sufficiently distinct"
                    },
                    "supported_classes": get_all_classes()
                }
            predicted_class = all_classes[pred_idx] if pred_idx < len(all_classes) else "Unknown"
            disease_info = get_disease_detail(predicted_class)

            return {
                "model_status": "inferred_successfully",
                "model_loaded": True,
                "filename": filename,
                "message": f"Diagnosis completed with a {confidence}% model score.",
                "image_details": {
                    "dimensions": f"{img_width}x{img_height}",
                    "status": "Inference completed via MobileNetV2 architecture"
                },
                "prediction": disease_info["disease_name"] if disease_info else predicted_class,
                "confidence": confidence,
                "disease_info": disease_info,
                "supported_classes": get_all_classes()
            }

        raise RuntimeError(f"Model format '{model_path.suffix}' detected but inference runner requires configuration.")

    except Exception as exc:
        raise RuntimeError(f"Foliar neural diagnostic inference error: {exc}")
