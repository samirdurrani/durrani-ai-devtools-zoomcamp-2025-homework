"""
Health Check Route

Simple endpoint to verify the API is running and healthy.
"""

from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings


# Create a router for health endpoints
router = APIRouter(
    prefix="/api/v1/health",
    tags=["Health"]
)


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str
    services: dict


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Check API health status.
    
    Returns basic service information and status of components.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.app_version,
        services={
            "api": "operational",
            "websocket": "operational",
            "executor": "operational" if settings.enable_server_execution else "disabled"
        }
    )
