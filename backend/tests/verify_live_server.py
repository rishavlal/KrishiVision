"""
Live Server Verification Script for KrishiVision
Runs an in-process Uvicorn instance and executes live HTTP requests against all endpoints.
E-09: Isolates database operations using a temporary SQLite database, protecting backend/krishivision.db.
E-10: Computes genuine pass percentage, prints SUCCESS only on 100% pass, and returns non-zero exit code on failure.
"""

import sys
import os
import time
import threading
import requests
import io
import uuid
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# E-09: Configure an isolated project-local SQLite file before app imports.
test_db_file = BASE_DIR / "tests" / f".live_verify_{uuid.uuid4().hex}.db"
test_db_url = f"sqlite:///{test_db_file}"
os.environ["DATABASE_URL"] = test_db_url

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app.db.database as db_module
from app.db.database import Base, get_db

test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal
Base.metadata.create_all(bind=test_engine)

from app.main import app, seed_database
from app.core.config import settings
import uvicorn

# Override get_db dependency for FastAPI
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
seed_database()

PORT = 8019
BASE = f"http://127.0.0.1:{PORT}"


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="error")


def cleanup_temp_db():
    """Clean up the isolated verification database and SQLite sidecars."""
    try:
        test_engine.dispose()
        for suffix in ("", "-wal", "-shm", "-journal"):
            test_file = Path(f"{test_db_file}{suffix}")
            if test_file.exists():
                test_file.unlink()
    except Exception:
        pass


def main():
    print("=" * 65)
    print("  KRISHIVISION — LIVE SYSTEM VERIFICATION SUITE")
    print("=" * 65)
    print(f"Starting in-process Uvicorn test server on {BASE}...")

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(2.0)

    passed = 0
    total = 0

    def check(name, fn):
        nonlocal passed, total
        total += 1
        try:
            fn()
            passed += 1
            print(f"[PASS] {name}")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")

    # 1. Root
    def test_root():
        r = requests.get(f"{BASE}/")
        assert r.status_code == 200
        assert r.json()["status"] == "online"
    check("1. GET / (System Status & Root)", test_root)

    # 2. Health
    def test_health():
        r = requests.get(f"{BASE}/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ["ok", "degraded"]
        assert data["services"]["database"] == "connected"
        assert data["ready"] is False
        assert data["readiness"] == "not_ready"
        assert data["services"]["crop_recommendation_ml_model"] in ["loaded", "file_available", "missing"]
    check("2. GET /api/health (Health & Model Status)", test_health)

    # 3. Web Application
    def test_frontend():
        r = requests.get(f"{BASE}/app")
        assert r.status_code == 200
        assert "कृषिVision" in r.text
        assert "Random Forest" in r.text
    check("3. GET /app (Frontend Web Application)", test_frontend)

    # 4. Demo Status & Demo Login
    def test_demo_auth():
        status_r = requests.get(f"{BASE}/api/auth/demo-status")
        assert status_r.status_code == 200
        data = status_r.json()
        enabled = settings.APP_ENV == "development" and settings.DEMO_USER_ENABLED
        assert data["demo_enabled"] is enabled
        assert data["demo_username"] == (settings.DEMO_USER_USERNAME if enabled else None)

        login_r = requests.post(f"{BASE}/api/auth/demo-login")
        if enabled:
            assert login_r.status_code == 200
            assert login_r.json()["user"]["username"] == settings.DEMO_USER_USERNAME.lower()
        else:
            assert login_r.status_code == 403
    check("4. GET /api/auth/demo-status & POST /api/auth/demo-login", test_demo_auth)

    # 5. User Registration & JWT Authentication
    auth_token = None
    auth_username = None
    def test_auth():
        nonlocal auth_token, auth_username
        username = f"live_tester_{uuid.uuid4().hex[:10]}"
        auth_username = username
        payload = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "TestPassword@2026",
            "full_name": "Live Test Farmer",
            "farm_location": "Ranchi, Jharkhand",
            "farm_size_hectares": 3.5
        }
        r = requests.post(f"{BASE}/api/auth/register", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert "access_token" in data
        auth_token = data["access_token"]
        assert len(auth_token) > 10
    check("5. POST /api/auth/register (JWT Authentication)", test_auth)

    # 6. Crop Recommendation - Path A
    def test_crop_path_a():
        payload = {
            "nitrogen": 90.0,
            "phosphorus": 42.0,
            "potassium": 43.0,
            "temperature": 28.5,
            "humidity": 72.0,
            "ph": 6.5,
            "rainfall": 202.0,
            "location": "Jharkhand"
        }
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        r = requests.post(f"{BASE}/api/predict", json=payload, headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert data["crop"] in ["Rice", "Jute"]
        assert data["confidence"] > 0
        assert data["persisted"] is True
        assert len(data["alternatives"]) > 0
        print(f"       -> Predicted Crop: {data['crop']} ({data['confidence']}% model probability score) [Persisted: {data['persisted']}]")
    check("6. POST /api/predict (Path A: Random Forest Model)", test_crop_path_a)

    # 7. Crop Guidance - Path B
    def test_crop_path_b():
        payload = {
            "location": "Jharkhand",
            "season": "Kharif",
            "water_availability": "Moderate",
            "irrigation_available": True
        }
        r = requests.post(f"{BASE}/api/crop-guidance", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["soil_test_required"] is True
        assert len(data["recommendations"]) > 0
        assert data["persisted"] is True
        assert data["record_id"] is not None
        print(f"       -> Rule matches found: {len(data['recommendations'])} crops")
    check("7. POST /api/crop-guidance (Path B: Agro-Climatic Guidance)", test_crop_path_b)

    # 8. Plant Disease Classes Catalog
    def test_disease_classes():
        r = requests.get(f"{BASE}/api/disease/classes")
        assert r.status_code == 200
        classes = r.json()
        assert len(classes) == 27
        print(f"       -> Validated {len(classes)} disease conditions across 6 species")
    check("8. GET /api/disease/classes (27 Classes Catalog)", test_disease_classes)

    # 9. Plant Disease Leaf Upload & Preprocessing
    def test_disease_upload():
        img = Image.new("RGB", (300, 300), color=(34, 139, 34))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        files = {"file": ("foliar_sample.jpg", buf, "image/jpeg")}
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        r = requests.post(f"{BASE}/api/disease/predict", files=files, headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert data["image_details"]["dimensions"] == "224x224"
        assert data["model_loaded"] is True
        assert data["prediction"] is not None
        assert data["persisted"] is True
        assert data["confidence"] is not None and data["confidence"] > 0
        print(f"       -> Predicted Disease: {data['prediction']} ({data['confidence']}% model score) [Persisted: {data['persisted']}]")
    check("9. POST /api/disease/predict (Foliar Image Upload & MobileNetV2)", test_disease_upload)

    # 10. Prediction History
    def test_history():
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        r = requests.get(f"{BASE}/api/history", headers=headers)
        assert r.status_code == 200
        records = r.json()
        assert len(records) > 0
        print(f"       -> Retrieved {len(records)} persisted prediction records")
    check("10. GET /api/history (Unified Database History)", test_history)

    # 11. Analytics Summary
    def test_analytics():
        r = requests.get(f"{BASE}/api/analytics/summary")
        assert r.status_code == 200
        data = r.json()
        assert data["total_predictions"] > 0
        assert len(data["crop_distribution"]) > 0
        assert "inference" in data["system_status"].lower()
        print(f"       -> Soil Health Index: {data['average_soil_health_index']}%, Crops logged: {len(data['crop_distribution'])}")
    check("11. GET /api/analytics/summary (Soil & Crop Analytics)", test_analytics)

    # 12. Password Change & User Stats
    def test_change_password_and_stats():
        nonlocal auth_token
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        stats_r = requests.get(f"{BASE}/api/auth/stats", headers=headers)
        assert stats_r.status_code == 200
        assert "total_crop_predictions" in stats_r.json()

        cp_r = requests.post(f"{BASE}/api/auth/change-password", json={
            "current_password": "TestPassword@2026",
            "new_password": "UpdatedPassword@2026"
        }, headers=headers)
        assert cp_r.status_code == 200
        assert cp_r.json()["status"] == "success"
        assert requests.get(f"{BASE}/api/auth/me", headers=headers).status_code == 401
        login_r = requests.post(f"{BASE}/api/auth/login", json={
            "username": auth_username,
            "password": "UpdatedPassword@2026"
        })
        assert login_r.status_code == 200
        auth_token = login_r.json()["access_token"]
        assert requests.get(f"{BASE}/api/auth/me", headers={
            "Authorization": f"Bearer {auth_token}"
        }).status_code == 200
    check("12. POST /api/auth/change-password & GET /api/auth/stats", test_change_password_and_stats)

    # 13. Sample Foliar Assets
    def test_sample_assets():
        r = requests.get(f"{BASE}/assets/samples/tomato_leaf_sample.jpg")
        assert r.status_code == 200
        assert len(r.content) > 1000
    check("13. GET /assets/samples/tomato_leaf_sample.jpg (Instant Benchmark Leaf)", test_sample_assets)

    # 14. Landing Page
    def test_landing():
        r = requests.get(f"{BASE}/landing")
        assert r.status_code == 200
        assert "कृषिVision" in r.text

        r_browser = requests.get(f"{BASE}/", headers={"Accept": "text/html,application/xhtml+xml"})
        assert r_browser.status_code == 200
        assert "Launch Portal" in r_browser.text
    check("14. GET /landing & GET / (Browser Landing Page)", test_landing)

    # 15. Server-side Logout Revocation
    def test_logout():
        nonlocal auth_token
        username = f"logout_tester_{uuid.uuid4().hex[:8]}"
        register_r = requests.post(f"{BASE}/api/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "TestPassword@2026"
        })
        assert register_r.status_code == 201
        token = register_r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        logout_r = requests.post(f"{BASE}/api/auth/logout", headers=headers)
        assert logout_r.status_code == 200
        assert requests.get(f"{BASE}/api/auth/me", headers=headers).status_code == 401
    check("15. POST /api/auth/logout (Token Revocation)", test_logout)

    # Calculate exact success percentage
    pct = (passed / total * 100.0) if total > 0 else 0.0
    all_passed = (passed == total and total > 0)
    result_status = "SUCCESS" if all_passed else "FAILURE"

    print("=" * 65)
    print(f"VERIFICATION RESULTS: {passed} / {total} CHECKS PASSED ({pct:.1f}% - {result_status})")
    print("=" * 65)

    cleanup_temp_db()

    # Exit with non-zero code if any check failed
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
