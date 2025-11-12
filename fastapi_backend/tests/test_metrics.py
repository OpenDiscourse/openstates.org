"""Tests for metrics endpoints."""
from fastapi.testclient import TestClient


def test_prometheus_metrics(client: TestClient):
    """Test Prometheus metrics endpoint."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")

    # Check for some expected metrics
    content = response.text
    assert "http_requests_total" in content or "python_info" in content
