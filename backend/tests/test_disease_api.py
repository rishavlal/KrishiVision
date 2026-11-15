"""
Automated Unit Tests for Plant Disease Module & Preprocessing
"""

import io
from PIL import Image
import pytest
from app.ml.plant_disease.disease_catalog import get_all_classes, get_disease_detail, DISEASE_CATALOG
from app.ml.plant_disease.classifier import validate_and_preprocess_image, predict_leaf_disease


def test_disease_catalog_classes_count():
    """Verify all 27 PlantVillage classes are fully populated."""
    classes = get_all_classes()
    assert len(classes) == 27
    assert len(DISEASE_CATALOG) == 27

    # Check species representation
    plants = {c["plant_name"] for c in classes}
    expected_species = {"Tomato", "Potato", "Corn (Maize)", "Apple", "Grape", "Bell Pepper"}
    assert expected_species == plants


def test_disease_treatment_structure():
    """Verify treatments contain 3-tier actionable regimens."""
    tomato_early_blight = get_disease_detail("Tomato___Early_blight")
    assert tomato_early_blight is not None
    assert "treatments" in tomato_early_blight
    assert "organic" in tomato_early_blight["treatments"]
    assert "chemical" in tomato_early_blight["treatments"]
    assert "cultural" in tomato_early_blight["treatments"]
    assert len(tomato_early_blight["symptoms"]) > 20


def test_image_preprocessing_pipeline():
    """Test image validation, RGB conversion, and 224x224 resize."""
    # Create test synthetic image in memory
    raw_img = Image.new("RGBA", (500, 400), color=(34, 139, 34, 255))
    buf = io.BytesIO()
    raw_img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    processed_img = validate_and_preprocess_image(img_bytes, "test_leaf.png")
    assert processed_img.size == (224, 224)
    assert processed_img.mode == "RGB"


@pytest.mark.parametrize("image_format,extension", [
    ("JPEG", ".jpg"),
    ("PNG", ".png"),
    ("WEBP", ".webp"),
])
def test_supported_decoded_image_formats(image_format, extension):
    raw_img = Image.new("RGB", (40, 35), color=(34, 139, 34))
    buf = io.BytesIO()
    raw_img.save(buf, format=image_format)

    processed_img = validate_and_preprocess_image(buf.getvalue(), f"leaf{extension}")
    assert processed_img.size == (224, 224)
    assert processed_img.mode == "RGB"


def test_gif_is_rejected_even_with_jpeg_filename():
    raw_img = Image.new("RGB", (40, 35), color=(34, 139, 34))
    buf = io.BytesIO()
    raw_img.save(buf, format="GIF")

    with pytest.raises(ValueError, match="Unsupported image format: GIF"):
        validate_and_preprocess_image(buf.getvalue(), "mislabelled.jpg")


def test_corrupted_image_rejection():
    """Verify corrupted bytes raise ValueError."""
    corrupted_bytes = b"not_an_image_file_content_123456"
    with pytest.raises(ValueError) as exc:
        validate_and_preprocess_image(corrupted_bytes, "corrupt.jpg")
    assert "not a valid image" in str(exc.value)


def test_disease_model_inference():
    """Verify trained MobileNetV2 neural model loads and executes genuine inference."""
    raw_img = Image.new("RGB", (250, 250), color=(50, 180, 50))
    buf = io.BytesIO()
    raw_img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    result = predict_leaf_disease(img_bytes, "leaf.jpg")
    assert "model_status" in result
    assert result["model_loaded"] is True
    assert result["model_status"] == "inferred_successfully"
    assert result["prediction"] is not None
    assert result["confidence"] is not None
    assert result["confidence"] > 0
    assert result["disease_info"] is not None
    assert len(result["supported_classes"]) == 27
