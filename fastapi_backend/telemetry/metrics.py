"""Prometheus metrics configuration."""
import logging
from typing import Optional

from prometheus_client import Counter, Histogram, Gauge, REGISTRY, generate_latest
from opentelemetry import metrics as otel_metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import Resource

from fastapi_backend.config.settings import settings

logger = logging.getLogger(__name__)

# Prometheus metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"]
)

proxy_requests_total = Counter(
    "proxy_requests_total",
    "Total number of proxied requests",
    ["backend", "method", "status_code"]
)

proxy_request_duration_seconds = Histogram(
    "proxy_request_duration_seconds",
    "Proxy request duration in seconds",
    ["backend", "method"]
)

error_counter = Counter(
    "errors_total",
    "Total number of errors",
    ["error_type", "endpoint"]
)


def setup_metrics() -> Optional[MeterProvider]:
    """Configure OpenTelemetry metrics with Prometheus exporter."""
    if not settings.prometheus_enabled:
        logger.info("Prometheus metrics are disabled")
        return None

    try:
        # Create resource
        resource = Resource.create({
            "service.name": settings.otel_service_name,
            "service.version": settings.app_version,
        })

        # Create Prometheus metric reader
        prometheus_reader = PrometheusMetricReader()

        # Create meter provider
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[prometheus_reader]
        )

        # Set global meter provider
        otel_metrics.set_meter_provider(meter_provider)

        logger.info("Prometheus metrics configured successfully")
        return meter_provider

    except Exception as e:
        logger.error(f"Failed to configure Prometheus metrics: {e}")
        return None


def get_prometheus_metrics():
    """Get Prometheus metrics in text format."""
    return generate_latest(REGISTRY)
