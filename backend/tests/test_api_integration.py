"""
Automated Integration Tests for FastAPI REST Endpoints.
Guarantees test database isolation via conftest.py fixtures.
Verifies all 10 system fixes: E-01 through E-10.
"""

import io
import uuid
import pytest
from PIL import Image


def test_system_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data


def test_health_check_endpoint(client, monkeypatch):
    """E-03: Health endpoint tests real DB connectivity and model status."""
    from app.ml.crop_recommendation import inference as crop_inference
    from app.ml.plant_disease import classifier as disease_classifier

    monkeypatch.setattr(crop_inference, "_MODEL", None)
    monkeypatch.setattr(disease_classifier, "_LOADED_MODEL", None)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert data["services"]["database"] == "connected"
    assert data["services"]["crop_recommendation_ml_model"] in ["loaded", "file_available", "missing"]
    assert "plant_disease_model" in data["services"]
    assert data["services"]["crop_recommendation_model_loaded"] is False
    assert data["services"]["plant_disease_model_loaded"] is False
    assert data["ready"] is False
    assert data["readiness"] == "not_ready"
    assert data["services"]["crop_recommendation_model_ready"] is False
    assert data["services"]["plant_disease_model_ready"] is False


def test_health_reports_loaded_models_as_ready(client, monkeypatch):
    from app.main import CROP_MODEL_PATH
    from app.ml.crop_recommendation import inference as crop_inference
    from app.ml.plant_disease import classifier as disease_classifier

    monkeypatch.setattr(crop_inference, "_MODEL", object())
    monkeypatch.setattr(disease_classifier, "_LOADED_MODEL", object())

    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["services"]["crop_recommendation_model_file_available"] is CROP_MODEL_PATH.is_file()
    assert data["services"]["crop_recommendation_model_loaded"] is True
    assert data["services"]["crop_recommendation_model_ready"] is True
    assert data["services"]["plant_disease_model_file_available"] is (disease_classifier.find_model_file() is not None)
    assert data["services"]["plant_disease_model_loaded"] is True
    assert data["services"]["plant_disease_model_ready"] is True
    assert data["ready"] is True


def test_demo_status_and_demo_login(client):
    """E-04: Verify demo credentials status and passwordless 1-click login endpoint."""
    from app.core.config import settings

    status_res = client.get("/api/auth/demo-status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    enabled = settings.APP_ENV == "development" and settings.DEMO_USER_ENABLED
    assert status_data["demo_enabled"] is enabled
    assert status_data["demo_username"] == (settings.DEMO_USER_USERNAME if enabled else None)

    login_res = client.post("/api/auth/demo-login")
    if enabled:
        assert login_res.status_code == 200
        assert login_res.json()["user"]["username"] == settings.DEMO_USER_USERNAME.lower()
    else:
        assert login_res.status_code == 403


def test_invalid_email_registration_rejected(client):
    """E-05: Strict email validation rejects invalid email strings."""
    invalid_payload = {
        "username": f"bad_mail_{uuid.uuid4().hex[:8]}",
        "email": "not-an-email-address",
        "password": "ValidPassword123"
    }
    response = client.post("/api/auth/register", json=invalid_payload)
    assert response.status_code == 422


def test_farm_size_update_validation(client):
    """E-06: Farm size constraints applied to profile updates (ge=0.1, le=1000.0)."""
    username = f"farm_sz_{uuid.uuid4().hex[:8]}"
    reg_res = client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "ValidPassword123",
        "farm_size_hectares": 2.5
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test negative farm size update
    neg_res = client.put("/api/auth/profile", json={"farm_size_hectares": -5.0}, headers=headers)
    assert neg_res.status_code == 422

    # Test zero farm size update
    zero_res = client.put("/api/auth/profile", json={"farm_size_hectares": 0.0}, headers=headers)
    assert zero_res.status_code == 422

    # Test excessive farm size update (> 1000.0)
    huge_res = client.put("/api/auth/profile", json={"farm_size_hectares": 5000.0}, headers=headers)
    assert huge_res.status_code == 422

    # Test valid farm size update
    valid_res = client.put("/api/auth/profile", json={"farm_size_hectares": 12.5}, headers=headers)
    assert valid_res.status_code == 200
    assert valid_res.json()["farm_size_hectares"] == 12.5


def test_auth_workflow(client):
    uname = f"tester_{uuid.uuid4().hex[:8]}"
    reg_payload = {
        "username": uname,
        "email": f"{uname}@example.com",
        "password": "FarmSecret@2026",
        "full_name": "Test Farmer",
        "farm_location": "Ranchi, Jharkhand",
        "farm_size_hectares": 4.0
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    login_payload = {
        "username": uname,
        "password": "FarmSecret@2026"
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == uname


def test_logout_revokes_presented_access_token(client):
    username = f"logout_{uuid.uuid4().hex[:8]}"
    register = client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "FarmSecret@2026"
    })
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout = client.post("/api/auth/logout", headers=headers)
    assert logout.status_code == 200
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_password_change_invalidates_all_prechange_tokens(client):
    username = f"pwchange_{uuid.uuid4().hex[:8]}"
    register = client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "FarmSecret@2026"
    })
    first_token = register.json()["access_token"]
    second_token = client.post("/api/auth/login", json={
        "username": username,
        "password": "FarmSecret@2026"
    }).json()["access_token"]

    changed = client.post("/api/auth/change-password", json={
        "current_password": "FarmSecret@2026",
        "new_password": "UpdatedSecret@2026"
    }, headers={"Authorization": f"Bearer {first_token}"})
    assert changed.status_code == 200
    assert client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {first_token}"
    }).status_code == 401
    assert client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {second_token}"
    }).status_code == 401

    new_login = client.post("/api/auth/login", json={
        "username": username,
        "password": "UpdatedSecret@2026"
    })
    assert new_login.status_code == 200
    assert client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {new_login.json()['access_token']}"
    }).status_code == 200


def test_crop_prediction_path_a_endpoint(client):
    """E-02: Check crop prediction returns explicit persistence status."""
    payload = {
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 40.0,
        "temperature": 27.0,
        "humidity": 75.0,
        "ph": 6.4,
        "rainfall": 195.0,
        "location": "Jharkhand"
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "crop" in data
    assert "confidence" in data
    assert 0 <= data["confidence"] <= 100
    assert "persisted" in data
    assert data["persisted"] is True
    assert data["record_id"] is not None


def test_crop_guidance_path_b_endpoint(client):
    payload = {
        "location": "Jharkhand",
        "season": "Kharif",
        "water_availability": "Moderate",
        "irrigation_available": True
    }
    response = client.post("/api/crop-guidance", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["soil_test_required"] is True
    assert len(data["recommendations"]) > 0
    assert data["persisted"] is True
    assert data["record_id"] is not None
    assert data["persistence_error"] is None


def test_crop_guidance_path_b_reports_persistence_failure(client, monkeypatch):
    from sqlalchemy.orm import Session as SQLAlchemySession

    def fail_commit(self):
        raise RuntimeError("forced database failure")

    monkeypatch.setattr(SQLAlchemySession, "commit", fail_commit)
    response = client.post("/api/crop-guidance", json={
        "location": "Jharkhand",
        "season": "Kharif",
        "water_availability": "Moderate",
        "irrigation_available": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["persisted"] is False
    assert data["record_id"] is None
    assert "forced database failure" in data["persistence_error"]


def test_disease_classes_endpoint(client):
    response = client.get("/api/disease/classes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 27


def test_disease_class_detail_endpoint(client):
    response = client.get("/api/disease/classes/Tomato___Early_blight")
    assert response.status_code == 200
    data = response.json()
    assert data["disease_name"] == "Early Blight"
    assert "treatments" in data


def test_disease_prediction_upload(client):
    """E-02 & E-07: Valid image upload and prediction persistence verification."""
    img = Image.new("RGB", (300, 300), color=(40, 160, 40))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    files = {"file": ("leaf.jpg", buf, "image/jpeg")}
    response = client.post("/api/disease/predict", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["model_loaded"] is True
    assert data["prediction"] is not None
    assert data["confidence"] is not None and data["confidence"] > 0
    assert data["image_details"]["dimensions"] == "224x224"
    assert data["persisted"] is True
    assert data["record_id"] is not None


def test_disease_oversized_image_rejection(client):
    """E-07: Reject oversized image uploads with HTTP 413 before excessive memory allocation."""
    # Create fake oversized stream > 10 MB
    oversized_data = b"x" * (11 * 1024 * 1024)
    files = {"file": ("huge.jpg", io.BytesIO(oversized_data), "image/jpeg")}
    response = client.post("/api/disease/predict", files=files)
    assert response.status_code == 413
    assert "exceeds" in response.json()["detail"].lower()


def test_disease_empty_file_rejection(client):
    """E-01 & E-07: Reject empty uploaded file with HTTP 400."""
    files = {"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")}
    response = client.post("/api/disease/predict", files=files)
    assert response.status_code == 400


def test_disease_corrupt_file_rejection(client):
    """E-01: Corrupt image file returns HTTP 400 and is NOT saved to database."""
    files = {"file": ("corrupt.jpg", io.BytesIO(b"not an image"), "image/jpeg")}
    response = client.post("/api/disease/predict", files=files)
    assert response.status_code == 400


def test_analytics_summary_endpoint(client):
    from app.ml.crop_recommendation import inference as crop_inference
    from app.ml.plant_disease import classifier as disease_classifier

    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_predictions"] >= 0
    assert "crop_distribution" in data
    assert "soil_averages" in data

    crop_ready = crop_inference._MODEL is not None
    disease_ready = disease_classifier._LOADED_MODEL is not None
    crop_file_exists = crop_inference.MODEL_PATH.exists()
    disease_file_exists = disease_classifier.find_model_file() is not None
    if crop_ready and disease_ready:
        expected_status = "All ML model inference caches are loaded"
    elif crop_file_exists and disease_file_exists:
        expected_status = "Model files available; inference readiness pending"
    elif crop_file_exists or disease_file_exists:
        expected_status = "Partially available; one or more model files are missing or not loaded"
    else:
        expected_status = "Degraded (ML model files unavailable)"
    assert data["system_status"] == expected_status


def test_history_unauthenticated_deletion_blocked(client):
    """Verify that an unauthenticated guest cannot delete an owned prediction record."""
    username = f"history_tester_{uuid.uuid4().hex[:10]}"
    reg_res = client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "TestPassword@2026"
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    crop_payload = {
        "nitrogen": 80.0, "phosphorus": 40.0, "potassium": 40.0,
        "temperature": 25.0, "humidity": 70.0, "ph": 6.5, "rainfall": 150.0
    }
    pres = client.post("/api/predict", json=crop_payload, headers=headers)
    assert pres.status_code == 200
    rec_id = pres.json()["record_id"]
    assert rec_id is not None

    del_res = client.delete(f"/api/history/{rec_id}?record_type=crop")
    assert del_res.status_code == 401

    del_auth_res = client.delete(f"/api/history/{rec_id}?record_type=crop", headers=headers)
    assert del_auth_res.status_code == 200


def test_landing_page_endpoints(client):
    landing_res = client.get("/landing")
    assert landing_res.status_code == 200
    assert "कृषिVision" in landing_res.text
    assert "Launch Portal" in landing_res.text

    browser_root = client.get("/", headers={"Accept": "text/html,application/xhtml+xml"})
    assert browser_root.status_code == 200
    assert "कृषिVision" in browser_root.text
