"""Tests for proxy endpoints."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import httpx


def test_proxy_status(client: TestClient):
    """Test proxy status endpoint."""
    response = client.get("/api/proxy-status")
    assert response.status_code == 200

    data = response.json()
    assert "backend_url" in data
    assert "status" in data
    assert data["status"] == "operational"
    assert "features" in data
    assert isinstance(data["features"], list)


@pytest.mark.asyncio
async def test_proxy_request_success():
    """Test successful proxy request."""
    from fastapi_backend.api.proxy import proxy_request
    from fastapi import Request

    # Mock request
    mock_request = AsyncMock(spec=Request)
    mock_request.method = "GET"
    mock_request.headers = {}
    mock_request.query_params = {}
    mock_request.body = AsyncMock(return_value=b"")
    mock_request.state.correlation_id = "test-123"

    # Mock HTTP response
    mock_response = httpx.Response(
        status_code=200,
        content=b'{"test": "data"}',
        headers={"content-type": "application/json"}
    )

    with patch("fastapi_backend.api.proxy.get_http_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client

        response = await proxy_request(mock_request, "test/path")

        assert response.status_code == 200
        mock_client.request.assert_called_once()
