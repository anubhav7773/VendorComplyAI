# apps/api/tests/test_health_router.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_head_health_root():
    """Verifies that HEAD /health returns HTTP 200 with zero payload and keep-alive headers."""
    response = client.head("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Uptime-Status") == "ALIVE"
    assert "no-cache" in response.headers.get("Cache-Control", "")
    assert len(response.content) == 0


def test_get_health_root():
    """Verifies that GET /health returns HTTP 200 with complete JSON metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert "service" in data
    assert "environment" in data
    assert data.get("uptime_robot") == "configured"


def test_head_health_api_v1():
    """Verifies that HEAD /api/v1/health also returns HTTP 200 with zero payload."""
    response = client.head("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("X-Uptime-Status") == "ALIVE"
    assert len(response.content) == 0


def test_get_health_api_v1():
    """Verifies that GET /api/v1/health returns HTTP 200 with valid JSON response."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"


def test_cors_dynamic_regex():
    """Verifies that CORS middleware dynamically accepts custom domains and localhost."""
    origins_to_test = [
        "https://vendorcomply.asiverticals.me",
        "https://staging.asiverticals.me",
        "https://vendorcomply.pages.dev",
        "https://preview-123.pages.dev",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    for origin in origins_to_test:
        response = client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == origin, (
            f"Failed for origin: {origin}"
        )
