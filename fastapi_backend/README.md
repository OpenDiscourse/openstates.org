# FastAPI Backend with Proxy and Observability

A full-featured FastAPI backend service with built-in proxy capabilities, comprehensive observability, telemetry, and OpenTelemetry integration.

## Features

### Core Features
- **FastAPI Framework**: Modern, fast, async Python web framework
- **Reverse Proxy**: Forward requests to Django backend with full header/param support
- **Health Checks**: Multiple health check endpoints for Kubernetes and monitoring
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

### Observability & Telemetry
- **OpenTelemetry Integration**: Full distributed tracing support
  - Automatic instrumentation for FastAPI and HTTPX
  - OTLP exporter for sending traces to collectors
  - Span creation for all requests and proxy calls
  
- **Prometheus Metrics**: Comprehensive metrics collection
  - HTTP request counters and histograms
  - Request duration tracking
  - In-progress request gauges
  - Proxy-specific metrics
  - Error counters by type
  
- **Structured Logging**: JSON-formatted logs with:
  - Correlation IDs for request tracking
  - Trace and span ID integration
  - Configurable log levels
  - Context-aware logging

### Middleware
- **Observability Middleware**: Tracks all requests with metrics, traces, and logs
- **Rate Limiting**: In-memory rate limiting with configurable limits
- **CORS Support**: Configurable cross-origin resource sharing

## Quick Start

### Running Locally

1. Install dependencies:
```bash
poetry install
```

2. Run the application:
```bash
python -m fastapi_backend.main
```

Or using uvicorn directly:
```bash
uvicorn fastapi_backend.main:app --reload --port 8001
```

### Running with Docker

Build and run:
```bash
docker build -f fastapi_backend/Dockerfile -t openstates-fastapi .
docker run -p 8001:8001 openstates-fastapi
```

### Running with Docker Compose

```bash
docker-compose up fastapi
```

## Configuration

Configuration is managed through environment variables or a `.env` file:

### Application Settings
- `DEBUG`: Enable debug mode (default: `False`)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8001`)

### Backend Settings
- `DJANGO_BACKEND_URL`: URL of Django backend (default: `http://django:8000`)

### OpenTelemetry Settings
- `OTEL_ENABLED`: Enable OpenTelemetry (default: `True`)
- `OTEL_SERVICE_NAME`: Service name for tracing (default: `openstates-fastapi`)
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OTLP collector endpoint (optional)
- `OTEL_EXPORTER_OTLP_INSECURE`: Use insecure connection (default: `True`)

### Prometheus Settings
- `PROMETHEUS_ENABLED`: Enable Prometheus metrics (default: `True`)
- `PROMETHEUS_PORT`: Metrics port (default: `9090`)

### Logging Settings
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `LOG_FORMAT`: Log format - `json` or `text` (default: `json`)

### Rate Limiting
- `RATE_LIMIT_ENABLED`: Enable rate limiting (default: `True`)
- `RATE_LIMIT_REQUESTS`: Max requests per window (default: `100`)
- `RATE_LIMIT_WINDOW`: Time window in seconds (default: `60`)

## API Endpoints

### Health & Status
- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed health with dependency checks
- `GET /api/health/ready` - Kubernetes readiness probe
- `GET /api/health/live` - Kubernetes liveness probe
- `GET /api/status/telemetry` - Telemetry configuration status

### Metrics
- `GET /api/metrics` - Prometheus metrics endpoint

### Proxy
- `GET/POST/PUT/DELETE /proxy/{path}` - Proxy requests to Django backend
- `GET /api/proxy-status` - Proxy configuration and status

### Documentation
- `GET /api/docs` - Interactive API documentation (Swagger UI)
- `GET /api/redoc` - Alternative API documentation (ReDoc)
- `GET /api/openapi.json` - OpenAPI schema

### Root
- `GET /` - Service information and available endpoints

## Observability Setup

### OpenTelemetry with Jaeger

1. Run Jaeger for tracing:
```bash
docker run -d \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

2. Configure the service:
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_ENABLED=true
```

3. Access Jaeger UI at http://localhost:16686

### Prometheus

1. Configure Prometheus to scrape metrics:
```yaml
scrape_configs:
  - job_name: 'openstates-fastapi'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/api/metrics'
```

2. Access metrics at http://localhost:8001/api/metrics

### Grafana Dashboard

Import the provided Grafana dashboard for visualization:
- HTTP request rates
- Request duration percentiles
- Error rates
- Proxy performance
- Active requests

## Testing

Run tests:
```bash
pytest fastapi_backend/tests/
```

Run with coverage:
```bash
pytest --cov=fastapi_backend fastapi_backend/tests/
```

## Architecture

```
┌─────────────────┐
│   Client        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  FastAPI Backend                        │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Middleware Stack                │  │
│  │  • CORS                          │  │
│  │  • Rate Limiting                 │  │
│  │  • Observability                 │  │
│  │  • OpenTelemetry                 │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  API Endpoints                   │  │
│  │  • Health Checks                 │  │
│  │  • Metrics                       │  │
│  │  • Proxy                         │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Telemetry                       │  │
│  │  • Tracing (OpenTelemetry)      │  │
│  │  • Metrics (Prometheus)          │  │
│  │  • Logging (Structured)          │  │
│  └──────────────────────────────────┘  │
└───────────┬─────────────────────────────┘
            │
            ▼
   ┌────────────────┐
   │ Django Backend │
   └────────────────┘
```

## Metrics Available

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_in_progress` - Active requests gauge
- `proxy_requests_total` - Total proxied requests
- `proxy_request_duration_seconds` - Proxy request duration
- `errors_total` - Total errors by type

## Development

### Code Structure
```
fastapi_backend/
├── __init__.py
├── main.py                 # Main application
├── config/                 # Configuration
│   ├── __init__.py
│   └── settings.py         # Settings management
├── api/                    # API endpoints
│   ├── __init__.py
│   ├── health.py           # Health checks
│   ├── metrics.py          # Metrics endpoint
│   └── proxy.py            # Proxy endpoints
├── middleware/             # Middleware components
│   ├── __init__.py
│   ├── observability.py    # Observability middleware
│   └── rate_limit.py       # Rate limiting
├── telemetry/              # Telemetry configuration
│   ├── __init__.py
│   ├── tracing.py          # OpenTelemetry tracing
│   ├── metrics.py          # Prometheus metrics
│   └── logging_config.py   # Structured logging
└── tests/                  # Tests
    ├── __init__.py
    ├── conftest.py
    ├── test_health.py
    ├── test_metrics.py
    ├── test_proxy.py
    └── test_root.py
```

### Adding New Endpoints

1. Create a new router in `api/` directory
2. Add endpoint handlers
3. Include router in `main.py`
4. Add tests in `tests/` directory

### Contributing

1. Follow existing code structure
2. Add tests for new features
3. Update documentation
4. Run linting: `flake8 fastapi_backend/`
5. Format code: `black fastapi_backend/`

## License

Same as parent project.
