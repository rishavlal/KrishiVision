from .auth import router as auth_router
from .crop import router as crop_router
from .disease import router as disease_router
from .history import router as history_router
from .analytics import router as analytics_router

__all__ = ["auth_router", "crop_router", "disease_router", "history_router", "analytics_router"]
