"""Proxy endpoints to forward requests to Django backend."""
import logging
import time
from typing import Optional

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import httpx

from fastapi_backend.config.settings import settings
from fastapi_backend.telemetry.metrics import proxy_requests_total, proxy_request_duration_seconds
from fastapi_backend.telemetry.tracing import get_tracer

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)
router = APIRouter(tags=["Proxy"])


# HTTP client for proxying
http_client = None


def get_http_client():
    """Get or create HTTP client."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    return http_client


async def proxy_request(
    request: Request,
    path: str,
    method: Optional[str] = None,
) -> Response:
    """Proxy a request to the Django backend."""
    start_time = time.time()
    method = method or request.method
    
    # Build target URL
    target_url = f"{settings.django_backend_url}/{path}"
    
    with tracer.start_as_current_span(
        f"proxy_{method}_{path}",
        attributes={
            "proxy.backend": "django",
            "proxy.method": method,
            "proxy.path": path,
            "proxy.url": target_url,
        }
    ) as span:
        try:
            # Get HTTP client
            client = get_http_client()
            
            # Prepare headers (exclude host header)
            headers = dict(request.headers)
            headers.pop("host", None)
            
            # Add correlation ID
            if hasattr(request.state, "correlation_id"):
                headers["X-Correlation-ID"] = request.state.correlation_id
            
            # Get request body
            body = await request.body()
            
            # Forward request
            logger.info(f"Proxying {method} request to {target_url}")
            
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                params=dict(request.query_params),
                content=body,
            )
            
            # Record metrics
            duration = time.time() - start_time
            proxy_requests_total.labels(
                backend="django",
                method=method,
                status_code=response.status_code
            ).inc()
            
            proxy_request_duration_seconds.labels(
                backend="django",
                method=method
            ).observe(duration)
            
            # Add span attributes
            span.set_attribute("proxy.status_code", response.status_code)
            span.set_attribute("proxy.duration_ms", duration * 1000)
            
            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type", "application/octet-stream")
            )
        
        except httpx.TimeoutException as e:
            duration = time.time() - start_time
            span.record_exception(e)
            logger.error(f"Timeout proxying request to {target_url}: {e}")
            raise HTTPException(status_code=504, detail="Gateway timeout")
        
        except httpx.RequestError as e:
            duration = time.time() - start_time
            span.record_exception(e)
            logger.error(f"Error proxying request to {target_url}: {e}")
            raise HTTPException(status_code=502, detail="Bad gateway")
        
        except Exception as e:
            duration = time.time() - start_time
            span.record_exception(e)
            logger.error(f"Unexpected error proxying request: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")


@router.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_endpoint(request: Request, path: str):
    """Generic proxy endpoint."""
    return await proxy_request(request, path)


@router.get("/api/proxy-status")
async def proxy_status():
    """Get proxy configuration and status."""
    return {
        "backend_url": settings.django_backend_url,
        "status": "operational",
        "features": [
            "request_forwarding",
            "response_streaming",
            "header_forwarding",
            "query_param_forwarding",
            "tracing",
            "metrics",
        ]
    }
