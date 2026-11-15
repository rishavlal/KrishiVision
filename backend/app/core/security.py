"""
KrishiVision Security & Token Management
=========================================
Robust authentication module supporting PBKDF2-HMAC-SHA256 password hashing
and signed JSON Web Tokens (compatible with both PyJWT and standard library HMAC).
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import settings
from ..db.database import get_db
from ..db.models import User, RevokedAccessToken, UserTokenInvalidation

# Optional PyJWT with graceful fallback
try:
    import jwt
    HAS_PYJWT = True
except ImportError:
    HAS_PYJWT = False


security_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Password Hashing (PBKDF2-HMAC-SHA256)
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Generate salted PBKDF2-HMAC-SHA256 password hash."""
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored salt$hash format."""
    try:
        salt, expected_hash = hashed_password.split("$", 1)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()
        return hmac.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT Token Generation & Verification
# ---------------------------------------------------------------------------

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create signed access token with timezone-aware UTC timestamps."""
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "iat": now_utc.timestamp(),
        "exp": int(expire.timestamp()),
        "jti": secrets.token_urlsafe(16),
    })

    if HAS_PYJWT:
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Pure Python signed HMAC-SHA256 token fallback
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
    signing_input = f"{header}.{payload}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{header}.{payload}.{sig_b64}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify signed token."""
    if HAS_PYJWT:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except Exception:
            return None

    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()

        # Add base64 padding
        pad = len(sig_b64) % 4
        if pad:
            sig_b64 += "=" * (4 - pad)
        actual_sig = base64.urlsafe_b64decode(sig_b64.encode())

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        # Decode payload
        p_pad = len(payload_b64) % 4
        if p_pad:
            payload_b64 += "=" * (4 - p_pad)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode()).decode())

        # Check expiration
        if "exp" in payload and payload["exp"] < int(time.time()):
            return None

        return payload
    except Exception:
        return None


def _is_token_invalid(token: str, payload: Dict[str, Any], user_id: int, db: Session) -> bool:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    revoked = db.query(RevokedAccessToken).filter(
        RevokedAccessToken.token_hash == token_hash
    ).first()
    if revoked:
        return True

    invalidation = db.query(UserTokenInvalidation).filter(
        UserTokenInvalidation.user_id == user_id
    ).first()
    if invalidation is None:
        return False

    issued_at = payload.get("iat")
    if issued_at is None:
        return True
    try:
        return float(issued_at) <= invalidation.invalid_before
    except (TypeError, ValueError):
        return True


def revoke_access_token(token: str, payload: Dict[str, Any], db: Session) -> None:
    """Persist a one-token revocation until its signed expiration time."""
    expires_at = payload.get("exp")
    if expires_at is None:
        expires_at = time.time() + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    db.add(RevokedAccessToken(token_hash=token_hash, expires_at=float(expires_at)))
    db.commit()


def invalidate_user_tokens(user_id: int, db: Session) -> None:
    """Invalidate tokens issued before the current password-change time."""
    invalidation = db.query(UserTokenInvalidation).filter(
        UserTokenInvalidation.user_id == user_id
    ).first()
    if invalidation is None:
        db.add(UserTokenInvalidation(user_id=user_id, invalid_before=time.time()))
    else:
        invalidation.invalid_before = time.time()


# ---------------------------------------------------------------------------
# FastAPI Auth Dependencies
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Strict authentication dependency requiring valid Bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please login or provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject identifier format invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if _is_token_invalid(credentials.credentials, payload, user_id_int, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has been revoked.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id_int).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user account no longer exists.",
        )

    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Optional authentication: returns User if authenticated, else None for guest."""
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        return None
    if _is_token_invalid(credentials.credentials, payload, user_id_int, db):
        return None
    return db.query(User).filter(User.id == user_id_int).first()
