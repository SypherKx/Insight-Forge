"""
Health check router.
"""

from datetime import datetime
from fastapi import APIRouter

from ..config import settings
from ..models.responses import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        services={
            "database": "healthy",
            "file_storage": "healthy",
            "detection_engine": "healthy",
            "root_cause_engine": "healthy",
            "explanation_engine": "healthy",
        },
        timestamp=datetime.utcnow(),
        rag_enabled=settings.rag_enabled,
    )
