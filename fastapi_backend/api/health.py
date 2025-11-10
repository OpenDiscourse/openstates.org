"""Health check and status endpoints."""
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
import httpx

from fastapi_backend.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


class HealthStatus(BaseModel):
    """Health check response model."""
    
    status: str
    timestamp: str
    version: str
    service: str


class DetailedHealthStatus(BaseModel):
    """Detailed health check with dependencies."""
    
    status: str
    timestamp: str
    version: str
    service: str
    checks: Dict[str, Dict[str, Any]]


class TelemetryInfo(BaseModel):
    """Telemetry configuration info."""
    
    opentelemetry_enabled: bool
    prometheus_enabled: bool
    service_name: str
    log_level: str


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint."""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.app_version,
        service=settings.app_name,
    )


@router.get("/health/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check():
    """Detailed health check with dependency status."""
    checks = {}
    
    # Check Django backend
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.django_backend_url}/")
            checks["django_backend"] = {
                "status": "healthy" if response.status_code < 500 else "unhealthy",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
            }
    except Exception as e:
        checks["django_backend"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        logger.error(f"Django backend health check failed: {e}")
    
    # Overall status
    overall_status = "healthy"
    if any(check.get("status") == "unhealthy" for check in checks.values()):
        overall_status = "degraded"
    
    return DetailedHealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version=settings.app_version,
        service=settings.app_name,
        checks=checks,
    )


@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}


@router.get("/status/telemetry", response_model=TelemetryInfo)
async def telemetry_status():
    """Get telemetry configuration status."""
    return TelemetryInfo(
        opentelemetry_enabled=settings.otel_enabled,
        prometheus_enabled=settings.prometheus_enabled,
        service_name=settings.otel_service_name,
        log_level=settings.log_level,
    )
