"""
KrishiVision Authentication API Routes
======================================
User registration, login, profile inspection and updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user,
    invalidate_user_tokens,
    revoke_access_token,
    security_scheme,
)
from ..db.database import get_db
from ..db.models import User, CropPredictionRecord, DiseasePredictionRecord
from ..schemas.auth import UserRegister, UserLogin, UserResponse, UserUpdate, PasswordChange, Token
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """Register a new farmer account and issue JWT token."""
    clean_username = payload.username.lower().strip()
    clean_email = payload.email.lower().strip()

    if db.query(User).filter(User.username == clean_username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken. Please choose another."
        )

    if db.query(User).filter(User.email == clean_email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user = User(
        username=clean_username,
        email=clean_email,
        full_name=payload.full_name or payload.username.capitalize(),
        hashed_password=hash_password(payload.password),
        farm_location=payload.farm_location or "Jharkhand, India",
        farm_size_hectares=payload.farm_size_hectares or 2.5,
        phone_number=payload.phone_number
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate farmer credentials and issue access token."""
    login_id = payload.username.lower().strip()
    user = db.query(User).filter(
        (User.username == login_id) | (User.email == login_id)
    ).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/demo-status")
def get_demo_status():
    """Report demo login availability without exposing secrets."""
    from ..core.config import settings
    enabled = bool(settings.APP_ENV == "development" and settings.DEMO_USER_ENABLED)
    return {
        "demo_enabled": enabled,
        "demo_username": settings.DEMO_USER_USERNAME if enabled else None
    }


@router.post("/demo-login", response_model=Token)
def demo_login(db: Session = Depends(get_db)):
    """Authenticate configured development demo user if demo mode is enabled."""
    from ..core.config import settings
    if settings.APP_ENV != "development" or not settings.DEMO_USER_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo login is disabled in this environment."
        )

    demo_username = settings.DEMO_USER_USERNAME.lower().strip()
    user = db.query(User).filter(User.username == demo_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configured demo user '{demo_username}' was not found in the database."
        )

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get authenticated user profile details."""
    return current_user


@router.post("/logout")
def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke the presented access token server-side."""
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )
    revoke_access_token(credentials.credentials, payload, db)
    return {"status": "success", "message": "Access token revoked."}


@router.put("/profile", response_model=UserResponse)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile settings for the authenticated farmer."""
    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()
    if payload.farm_location is not None:
        current_user.farm_location = payload.farm_location.strip()
    if payload.farm_size_hectares is not None:
        current_user.farm_size_hectares = float(payload.farm_size_hectares)
    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number.strip()

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password")
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update farmer password securely."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect."
        )
    current_user.hashed_password = hash_password(payload.new_password)
    invalidate_user_tokens(current_user.id, db)
    db.commit()
    return {"status": "success", "message": "Password updated successfully."}


@router.get("/stats")
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve personal prediction statistics for the authenticated farmer."""
    crop_count = db.query(CropPredictionRecord).filter(CropPredictionRecord.user_id == current_user.id).count()
    disease_count = db.query(DiseasePredictionRecord).filter(DiseasePredictionRecord.user_id == current_user.id).count()
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "total_crop_predictions": crop_count,
        "total_disease_scans": disease_count,
        "member_since": current_user.created_at.strftime("%B %Y") if current_user.created_at else "Recently"
    }
