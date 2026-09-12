# apps/api/app/routers/health.py

from fastapi import APIRouter, Response, status
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.head("/health", status_code=status.HTTP_200_OK)
@router.head("/api/v1/health", status_code=status.HTTP_200_OK)
async def health_head():
    """
    Dedicated UptimeRobot 24/7 keep-alive endpoint.
    Returns HTTP 200 OK immediately with zero body payload and fast response headers
    to prevent Render free-tier containers from sleeping while consuming zero egress bandwidth.
    """
    return Response(
        content=b"",
        status_code=status.HTTP_200_OK,
        media_type="application/json",
        headers={
            "X-Uptime-Status": "ALIVE",
            "Cache-Control": "no-cache, no-store",
        },
    )


@router.get("/health", status_code=status.HTTP_200_OK)
@router.get("/api/v1/health", status_code=status.HTTP_200_OK)
async def health_get():
    """
    Standard JSON health check providing service metadata and environment status.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "uptime_robot": "configured",
    }
