# FastAPI Backend Integration Guide

This document describes the new FastAPI backend service that has been added to the OpenStates.org project.

## Overview

A full-featured FastAPI backend has been integrated into the OpenStates.org project, providing:

- **Reverse Proxy**: Forward requests to the Django backend
- **Observability**: Comprehensive monitoring with OpenTelemetry and Prometheus
- **Telemetry**: Distributed tracing, metrics collection, and structured logging
- **Health Checks**: Kubernetes-ready health and readiness probes
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Architecture

The FastAPI backend runs as a separate service alongside the existing Django application:

```
┌──────────────┐
│   Clients    │
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌─────────────────┐
│   Django     │  │ FastAPI Backend │
│   (Port 8000)│  │   (Port 8001)   │
└──────────────┘  └─────────┬───────┘
                            │
                   ┌────────┴─────────┐
                   │  Can proxy to    │
                   │  Django backend  │
                   └──────────────────┘
```

## Quick Start

### Using Docker Compose

The easiest way to run the FastAPI backend is with Docker Compose:

```bash
# Start all services including FastAPI
docker-compose up fastapi

# Or start everything
docker-compose up
```

The FastAPI service will be available at:
- API: http://localhost:8001
- Documentation: http://localhost:8001/api/docs
- Metrics: http://localhost:8001/api/metrics

### Running Locally

1. Install dependencies:
```bash
pip install fastapi uvicorn httpx pydantic pydantic-settings \
    opentelemetry-api opentelemetry-sdk \
    opentelemetry-instrumentation-fastapi \
    opentelemetry-instrumentation-httpx \
    opentelemetry-instrumentation-logging \
    opentelemetry-exporter-otlp-proto-grpc \
    opentelemetry-exporter-prometheus \
    prometheus-client
```

2. Set up environment (optional):
```bash
cp fastapi_backend/.env.example fastapi_backend/.env
# Edit .env file with your configuration
```

3. Run the server:
```bash
# Development mode with auto-reload
./fastapi_backend/run.sh --dev

# Or using Python directly
python -m uvicorn fastapi_backend.main:app --reload --port 8001

# Production mode
./fastapi_backend/run.sh
```

## Available Endpoints

### Core Endpoints

- `GET /` - Service information and available endpoints
- `GET /api/docs` - Interactive API documentation (Swagger UI)
- `GET /api/redoc` - Alternative API documentation (ReDoc)
- `GET /api/openapi.json` - OpenAPI schema

### Health & Status

- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed health with dependency checks
- `GET /api/health/ready` - Kubernetes readiness probe
- `GET /api/health/live` - Kubernetes liveness probe
- `GET /api/status/telemetry` - Telemetry configuration status

### Observability

- `GET /api/metrics` - Prometheus metrics endpoint

### Proxy

- `GET/POST/PUT/DELETE /proxy/{path}` - Forward requests to Django backend
- `GET /api/proxy-status` - Proxy configuration and status

## Configuration

Configuration is managed through environment variables or a `.env` file in the `fastapi_backend/` directory.

### Essential Settings

```bash
# Django backend URL (required)
DJANGO_BACKEND_URL=http://django:8000

# Server settings
HOST=0.0.0.0
PORT=8001
DEBUG=False
```

### Observability Settings

```bash
# OpenTelemetry
OTEL_ENABLED=true
OTEL_SERVICE_NAME=openstates-fastapi
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
OTEL_EXPORTER_OTLP_INSECURE=true

# Prometheus
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or 'text'
```

### Security & Rate Limiting

```bash
# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60  # seconds

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Observability Stack Setup

### 1. OpenTelemetry with Jaeger

Run Jaeger for distributed tracing:

```bash
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

Configure the FastAPI backend:
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_ENABLED=true
```

Access Jaeger UI at http://localhost:16686

### 2. Prometheus

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'openstates-fastapi'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/api/metrics'
    scrape_interval: 15s
```

### 3. Grafana Dashboard

Import a Grafana dashboard to visualize:
- HTTP request rates and durations
- Error rates by endpoint
- Proxy performance
- Active request gauges
- Custom business metrics

## Using the Proxy Feature

The FastAPI backend can proxy requests to the Django backend. This is useful for:
- Adding observability to Django requests
- Rate limiting
- Request/response transformation
- A/B testing
- Gradual migration

Example:
```bash
# Direct Django request
curl http://localhost:8000/some/path

# Proxied through FastAPI (with observability)
curl http://localhost:8001/proxy/some/path
```

## Monitoring & Metrics

### Available Metrics

The `/api/metrics` endpoint exposes:

- `http_requests_total` - Total HTTP requests by method, endpoint, and status
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_in_progress` - Active requests gauge
- `proxy_requests_total` - Total proxied requests
- `proxy_request_duration_seconds` - Proxy request duration
- `errors_total` - Errors by type and endpoint

### Structured Logging

All logs are output in JSON format with:
- Timestamp (UTC)
- Log level
- Logger name
- Correlation IDs for request tracking
- Trace and span IDs (when tracing is enabled)
- Contextual fields

Example log entry:
```json
{
  "timestamp": "2025-11-10T12:28:08.945313+00:00",
  "level": "INFO",
  "logger": "fastapi_backend.main",
  "message": "Starting OpenStates FastAPI Backend v1.0.0",
  "module": "main",
  "function": "lifespan",
  "line": 26
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest fastapi_backend/tests/

# Run with coverage
pytest --cov=fastapi_backend fastapi_backend/tests/

# Run specific test file
pytest fastapi_backend/tests/test_health.py -v
```

### Code Quality

```bash
# Linting
flake8 fastapi_backend/ --max-line-length=120

# Code formatting
black fastapi_backend/

# Type checking (optional)
mypy fastapi_backend/
```

### Project Structure

```
fastapi_backend/
├── __init__.py
├── main.py                     # Main FastAPI application
├── Dockerfile                  # Docker build file
├── README.md                   # Detailed documentation
├── .env.example                # Example configuration
├── run.sh                      # Quick start script
├── config/
│   ├── __init__.py
│   └── settings.py             # Pydantic settings
├── api/
│   ├── __init__.py
│   ├── health.py               # Health check endpoints
│   ├── metrics.py              # Metrics endpoints
│   └── proxy.py                # Proxy endpoints
├── middleware/
│   ├── __init__.py
│   ├── observability.py        # Metrics, tracing, logging
│   └── rate_limit.py           # Rate limiting
├── telemetry/
│   ├── __init__.py
│   ├── tracing.py              # OpenTelemetry tracing
│   ├── metrics.py              # Prometheus metrics
│   └── logging_config.py       # Structured logging
└── tests/
    ├── __init__.py
    ├── conftest.py             # Test fixtures
    ├── test_health.py
    ├── test_metrics.py
    ├── test_proxy.py
    └── test_root.py
```

## Deployment

### Docker

Build the image:
```bash
docker build -f fastapi_backend/Dockerfile -t openstates-fastapi .
```

Run the container:
```bash
docker run -p 8001:8001 \
  -e DJANGO_BACKEND_URL=http://django:8000 \
  -e OTEL_ENABLED=true \
  openstates-fastapi
```

### Kubernetes

Example deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-backend
  template:
    metadata:
      labels:
        app: fastapi-backend
    spec:
      containers:
      - name: fastapi
        image: openstates-fastapi:latest
        ports:
        - containerPort: 8001
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: DJANGO_BACKEND_URL
          value: "http://django-service:8000"
        - name: OTEL_ENABLED
          value: "true"
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://otel-collector:4317"
        livenessProbe:
          httpGet:
            path: /api/health/live
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health/ready
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Migration Strategy

If you want to gradually migrate from Django to FastAPI:

1. **Phase 1**: Run both services side-by-side (current state)
2. **Phase 2**: Route specific endpoints through FastAPI proxy
3. **Phase 3**: Implement new features in FastAPI
4. **Phase 4**: Migrate existing endpoints one by one
5. **Phase 5**: Full migration complete

## Troubleshooting

### Service Won't Start

Check:
1. Port 8001 is not already in use: `lsof -i :8001`
2. Dependencies are installed: `pip list | grep fastapi`
3. Environment variables are set correctly
4. Check logs for error messages

### Metrics Not Appearing

1. Verify Prometheus is configured correctly
2. Check `/api/metrics` endpoint is accessible
3. Verify `PROMETHEUS_ENABLED=true`
4. Check Prometheus scrape config and targets

### Tracing Not Working

1. Verify OTLP endpoint is accessible
2. Check `OTEL_ENABLED=true`
3. Verify `OTEL_EXPORTER_OTLP_ENDPOINT` is correct
4. Check Jaeger or trace collector is running

### High Memory Usage

1. Adjust rate limiting settings
2. Review log level (set to WARNING or ERROR in production)
3. Check for memory leaks in custom middleware
4. Monitor with metrics: `process_resident_memory_bytes`

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Run linting and tests before committing
5. Update this guide if adding new features

## Security Considerations

1. **Rate Limiting**: Enabled by default to prevent abuse
2. **CORS**: Configure `CORS_ORIGINS` for production
3. **Secrets**: Never commit secrets to version control
4. **Dependencies**: Regularly update dependencies for security patches
5. **Input Validation**: Pydantic models validate all inputs
6. **Headers**: Sensitive headers are not logged

## Performance Tips

1. **Async/Await**: All endpoints use async for better concurrency
2. **Connection Pooling**: HTTPX client reuses connections
3. **Caching**: Consider adding Redis for caching
4. **Load Balancing**: Use multiple replicas in Kubernetes
5. **CDN**: Serve static assets from CDN
6. **Database**: Use read replicas for heavy read workloads

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/openstates/issues/issues
- Documentation: See `fastapi_backend/README.md`
- Code: Located in `fastapi_backend/` directory

## License

Same as parent project (OpenStates.org).
