"""Metrics endpoints."""
import logging

from fastapi import APIRouter, Response

from fastapi_backend.telemetry.metrics import get_prometheus_metrics

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    metrics = get_prometheus_metrics()
    return Response(
        content=metrics,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
