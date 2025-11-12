"""Observability middleware for request tracking and metrics."""
import time
import uuid
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from fastapi_backend.telemetry.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress,
    error_counter,
)
from fastapi_backend.telemetry.tracing import get_tracer

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for observability: metrics, tracing, and logging."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with observability."""
        # Generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        # Track in-progress requests
        method = request.method
        endpoint = request.url.path
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Start timing
        start_time = time.time()

        # Create span for request
        with tracer.start_as_current_span(
            f"{method} {endpoint}",
            attributes={
                "http.method": method,
                "http.url": str(request.url),
                "http.route": endpoint,
                "correlation.id": correlation_id,
            }
        ) as span:
            try:
                # Process request
                response = await call_next(request)

                # Record metrics
                duration = time.time() - start_time
                status_code = response.status_code

                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()

                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

                # Add span attributes
                span.set_attribute("http.status_code", status_code)
                span.set_attribute("http.response_time_ms", duration * 1000)

                # Add correlation ID to response
                response.headers["X-Correlation-ID"] = correlation_id

                # Log request
                logger.info(
                    f"{method} {endpoint} {status_code}",
                    extra={
                        "extra_fields": {
                            "method": method,
                            "endpoint": endpoint,
                            "status_code": status_code,
                            "duration_ms": duration * 1000,
                            "correlation_id": correlation_id,
                        }
                    }
                )

                return response

            except Exception as e:
                # Record error metrics
                duration = time.time() - start_time
                error_counter.labels(
                    error_type=type(e).__name__,
                    endpoint=endpoint
                ).inc()

                # Add error to span
                span.record_exception(e)
                span.set_attribute("error", True)

                # Log error
                logger.error(
                    f"Error processing {method} {endpoint}: {e}",
                    exc_info=True,
                    extra={
                        "extra_fields": {
                            "method": method,
                            "endpoint": endpoint,
                            "error_type": type(e).__name__,
                            "duration_ms": duration * 1000,
                            "correlation_id": correlation_id,
                        }
                    }
                )

                raise

            finally:
                # Decrement in-progress requests
                http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
