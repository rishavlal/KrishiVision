"""
KrishiVision AI — Intelligent Crop Recommendation and Plant Disease Detection API
=================================================================================
Core FastAPI Application integrating Random Forest crop matchmaking,
rule-based preliminary guidance, foliar vision diagnostics, JWT authentication,
and SQLite database persistence.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.security import hash_password
from .db import database as db_manager
from .db.models import User, CropPredictionRecord
from .api import auth_router, crop_router, disease_router, history_router, analytics_router
from .ml.crop_recommendation.inference import MODEL_PATH as CROP_MODEL_PATH
from .ml.plant_disease.disease_catalog import DISEASE_CATALOG


def seed_database():
    """Ensure tables exist and seed an explicitly configured development demo user."""
    db_manager.init_db()
    if not settings.DEMO_USER_ENABLED:
        return

    db = db_manager.SessionLocal()
    try:
        demo_user = db.query(User).filter(User.username == settings.DEMO_USER_USERNAME).first()
        if not demo_user:
            demo_user = User(
                username=settings.DEMO_USER_USERNAME,
                email=settings.DEMO_USER_EMAIL,
                full_name=settings.DEMO_USER_NAME or None,
                hashed_password=hash_password(settings.DEMO_USER_PASSWORD),
                farm_location=settings.DEMO_USER_LOCATION or None,
                farm_size_hectares=settings.DEMO_USER_FARM_SIZE,
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan event handler for startup and shutdown."""
    seed_database()
    yield


app = FastAPI(
    title=settings.PROJECT_TITLE,
    description=(
        "Production-grade agricultural decision-support system featuring Random Forest "
        "crop matchmaking, preliminary agro-climatic guidance, and 27-class plant disease diagnostics."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Mount Static Frontend Assets & Directories
# ---------------------------------------------------------------------------
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


# ---------------------------------------------------------------------------
# Include API Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(crop_router)
app.include_router(disease_router)
app.include_router(history_router)
app.include_router(analytics_router)


# ---------------------------------------------------------------------------
# Root & System Status Endpoints
# ---------------------------------------------------------------------------
from fastapi import Request, Depends
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from .db.database import get_db
from .ml.crop_recommendation import inference as crop_inference
from .ml.plant_disease import classifier as disease_classifier

@app.get("/landing", include_in_schema=False)
def serve_landing_page():
    """Serve the agricultural AI landing page."""
    landing_file = FRONTEND_DIR / "landing.html"
    if landing_file.exists():
        return FileResponse(landing_file)
    return {"message": "Landing page not found"}


@app.get("/app", include_in_schema=False)
def serve_frontend_app():
    """Serve the single-page agricultural frontend dashboard application."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend index.html not found"}


@app.get("/")
def system_root(request: Request):
    """
    If requested by a browser (Accept: text/html), serve the stunning Landing Page!
    Otherwise, return system metadata and project status JSON for API tests.
    """
    accept = request.headers.get("accept", "")
    landing_file = FRONTEND_DIR / "landing.html"
    if "text/html" in accept and landing_file.exists():
        return FileResponse(landing_file)

    return {
        "service": "कृषिVision AI API",
        "official_title": settings.PROJECT_TITLE,
        "version": settings.VERSION,
        "status": "online",
        "documentation": "/docs",
        "landing_page": "/landing",
        "farmer_portal": "/app",
        "endpoints": {
            "health": "/api/health",
            "auth_register": "/api/auth/register",
            "auth_login": "/api/auth/login",
            "crop_predict_path_a": "/api/predict",
            "crop_guidance_path_b": "/api/crop-guidance",
            "disease_predict": "/api/disease/predict",
            "disease_classes": "/api/disease/classes",
            "history": "/api/history",
            "analytics_summary": "/api/analytics/summary"
        }
    }


@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """
    Accurately report system health, active database connectivity,
    model files, and cached inference readiness without loading models.
    """
    # 1. Verify actual database connectivity
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
        db_ok = True
    except Exception as db_err:
        db_status = f"disconnected: {db_err}"

    # A model file alone is not evidence that inference is ready. Health checks
    # intentionally inspect caches and paths without loading large model files.
    crop_model_loaded = crop_inference._MODEL is not None
    crop_model_file_available = CROP_MODEL_PATH.is_file()
    if crop_model_loaded:
        crop_model_status = "loaded"
    elif crop_model_file_available:
        crop_model_status = "file_available"
    else:
        crop_model_status = "missing"
    crop_model_ready = crop_model_loaded

    disease_model_file = disease_classifier.find_model_file()
    disease_model_loaded = disease_classifier._LOADED_MODEL is not None
    disease_model_file_available = disease_model_file is not None
    if disease_model_loaded:
        disease_model_status = "loaded"
    elif disease_model_file_available:
        disease_model_status = "file_available"
    else:
        disease_model_status = "missing"
    disease_model_ready = disease_model_loaded

    inference_ready = db_ok and crop_model_ready and disease_model_ready
    system_status = "ok" if inference_ready else "degraded"

    return {
        "status": system_status,
        "ready": inference_ready,
        "readiness": "ready" if inference_ready else "not_ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": db_status,
            "crop_recommendation_ml_model": crop_model_status,
            "crop_recommendation_model_file_available": crop_model_file_available,
            "crop_recommendation_model_loaded": crop_model_loaded,
            "crop_recommendation_model_ready": crop_model_ready,
            "crop_guidance_rule_engine": "active",
            "plant_disease_model": disease_model_status,
            "plant_disease_model_file_available": disease_model_file_available,
            "plant_disease_model_loaded": disease_model_loaded,
            "plant_disease_model_ready": disease_model_ready,
            "plant_disease_catalog": f"active ({len(DISEASE_CATALOG)} classes)",
            "authentication": "jwt_active"
        }
    }
