"""Tests for health check endpoints."""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test basic health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "service" in data


def test_readiness_check(client: TestClient):
    """Test Kubernetes readiness probe."""
    response = client.get("/api/health/ready")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ready"


def test_liveness_check(client: TestClient):
    """Test Kubernetes liveness probe."""
    response = client.get("/api/health/live")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "alive"


def test_telemetry_status(client: TestClient):
    """Test telemetry status endpoint."""
    response = client.get("/api/status/telemetry")
    assert response.status_code == 200

    data = response.json()
    assert "opentelemetry_enabled" in data
    assert "prometheus_enabled" in data
    assert "service_name" in data
    assert "log_level" in data
