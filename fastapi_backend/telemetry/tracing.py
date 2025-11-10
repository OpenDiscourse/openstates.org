"""OpenTelemetry tracing configuration."""
import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from fastapi_backend.config.settings import settings

logger = logging.getLogger(__name__)


def setup_tracing() -> Optional[TracerProvider]:
    """Configure OpenTelemetry tracing."""
    if not settings.otel_enabled:
        logger.info("OpenTelemetry tracing is disabled")
        return None

    try:
        # Create resource with service information
        resource = Resource.create({
            "service.name": settings.otel_service_name,
            "service.version": settings.app_version,
            "deployment.environment": "production" if not settings.debug else "development",
        })

        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)

        # Add OTLP exporter if endpoint is configured
        if settings.otel_exporter_otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(
                endpoint=settings.otel_exporter_otlp_endpoint,
                insecure=settings.otel_exporter_otlp_insecure,
            )
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
            logger.info(f"OTLP exporter configured with endpoint: {settings.otel_exporter_otlp_endpoint}")

        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)

        # Instrument HTTP clients
        HTTPXClientInstrumentor().instrument()

        # Instrument logging
        LoggingInstrumentor().instrument(set_logging_format=True)

        logger.info("OpenTelemetry tracing configured successfully")
        return tracer_provider

    except Exception as e:
        logger.error(f"Failed to configure OpenTelemetry tracing: {e}")
        return None


def instrument_app(app):
    """Instrument FastAPI application with OpenTelemetry."""
    if settings.otel_enabled:
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumented with OpenTelemetry")
        except Exception as e:
            logger.error(f"Failed to instrument FastAPI: {e}")


def get_tracer(name: str = __name__):
    """Get a tracer instance."""
    return trace.get_tracer(name)
