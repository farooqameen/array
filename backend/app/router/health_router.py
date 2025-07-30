"""
API routes for application health checks and status monitoring.

Provides endpoints for checking the health status of the application
and its dependencies.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from logger import logger
from models.api_models import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        HealthResponse: Simple status indicating the service is running.
    """
    try:
        return HealthResponse(status="healthy")
    except Exception as e:
        logger.error("Health check failed: %s", e, exc_info=True)
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": f"Service error: {e}"},
        )
