import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_health_endpoint():
    """
    Test unversioned GET /health endpoint.
    Spec Requirement:
    Response:
    {
      "status": "ok",
      "service": "recoverai-api",
      "version": "0.1.0"
    }
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "recoverai-api"
    assert data["version"] == "0.1.0"


def test_v1_health_endpoint():
    """
    Test versioned GET /api/v1/health endpoint.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "recoverai-api"
    assert data["version"] == "0.1.0"


def test_v1_detailed_health_endpoint():
    """
    Test versioned GET /api/v1/health/detailed endpoint.
    """
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "recoverai-api"
    assert "database" in data
    assert "redis" in data
