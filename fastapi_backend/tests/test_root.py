"""Tests for root endpoint."""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns service information."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "operational"
    assert "documentation" in data
    assert "health" in data
    assert "metrics" in data
    assert "telemetry" in data
    
    # Check telemetry info
    assert "opentelemetry" in data["telemetry"]
    assert "prometheus" in data["telemetry"]
