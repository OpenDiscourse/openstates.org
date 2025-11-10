"""Test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient

from fastapi_backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    from fastapi_backend.config import settings
    
    monkeypatch.setattr(settings.settings, "debug", True)
    monkeypatch.setattr(settings.settings, "otel_enabled", False)
    monkeypatch.setattr(settings.settings, "rate_limit_enabled", False)
    
    return settings.settings
