"""
Automated Unit Tests for Plant Disease Module & Preprocessing
"""

import io
from pathlib import Path
from PIL import Image, ImageDraw
import pytest
from app.ml.plant_disease.disease_catalog import get_all_classes, get_disease_detail, DISEASE_CATALOG
from app.ml.plant_disease.classifier import validate_and_preprocess_image, predict_leaf_disease

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "frontend" / "assets" / "samples"


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


@pytest.mark.parametrize("sample_name", [
    "tomato_leaf_sample.jpg",
    "potato_leaf_sample.jpg",
    "corn_leaf_sample.jpg",
])
def test_disease_model_inference(sample_name):
    """Verify trained MobileNetV2 neural model loads and executes genuine inference."""
    result = predict_leaf_disease((SAMPLE_DIR / sample_name).read_bytes(), sample_name)
    assert "model_status" in result
    assert result["model_loaded"] is True
    assert result["model_status"] == "inferred_successfully"
    assert result["prediction"] is not None
    assert result["confidence"] is not None
    assert result["confidence"] > 0
    assert result["disease_info"] is not None
    assert len(result["supported_classes"]) == 27


def test_portrait_image_is_rejected_before_model_inference():
    portrait = Image.new("RGB", (240, 240), color=(185, 198, 208))
    draw = ImageDraw.Draw(portrait)
    draw.ellipse((48, 25, 192, 190), fill=(214, 157, 122))
    draw.arc((80, 60, 160, 140), start=180, end=360, fill=(55, 42, 38), width=12)
    buffer = io.BytesIO()
    portrait.save(buffer, format="JPEG")

    with pytest.raises(ValueError, match="Invalid Image"):
        predict_leaf_disease(buffer.getvalue(), "portrait.jpg")


def test_document_image_is_rejected_before_model_inference():
    document = Image.new("RGB", (240, 240), color="white")
    draw = ImageDraw.Draw(document)
    for y in range(35, 205, 18):
        draw.line((28, y, 212, y), fill="black", width=2)
    buffer = io.BytesIO()
    document.save(buffer, format="JPEG")

    with pytest.raises(ValueError, match="Invalid Image"):
        predict_leaf_disease(buffer.getvalue(), "document.jpg")


def test_low_evidence_image_returns_uncertainty_without_a_disease():
    image = Image.new("RGB", (240, 240), color=(40, 160, 40))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")

    result = predict_leaf_disease(buffer.getvalue(), "flat-green.jpg")

    assert result["model_status"] == "uncertain_image"
    assert result["prediction"] is None
    assert result["disease_info"] is None
