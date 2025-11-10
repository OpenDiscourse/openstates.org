"""Main FastAPI application with observability and proxy."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fastapi_backend.config.settings import settings
from fastapi_backend.telemetry.logging_config import setup_logging
from fastapi_backend.telemetry.tracing import setup_tracing, instrument_app
from fastapi_backend.telemetry.metrics import setup_metrics
from fastapi_backend.middleware.observability import ObservabilityMiddleware
from fastapi_backend.middleware.rate_limit import RateLimitMiddleware
from fastapi_backend.api import health, metrics, proxy

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Setup telemetry
    tracer_provider = setup_tracing()
    meter_provider = setup_metrics()
    
    if tracer_provider:
        logger.info("Tracing initialized")
    if meter_provider:
        logger.info("Metrics initialized")
    
    logger.info(f"Application started on {settings.host}:{settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    
    # Cleanup HTTP client
    if proxy.http_client:
        await proxy.http_client.aclose()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Full-featured FastAPI backend with proxy, observability, and OpenTelemetry",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ObservabilityMiddleware)

# Instrument with OpenTelemetry
instrument_app(app)

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(proxy.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "documentation": "/api/docs",
        "health": "/api/health",
        "metrics": "/api/metrics",
        "telemetry": {
            "opentelemetry": settings.otel_enabled,
            "prometheus": settings.prometheus_enabled,
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with logging."""
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "extra_fields": {
                "path": request.url.path,
                "method": request.method,
                "error_type": type(exc).__name__,
            }
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "fastapi_backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
