from fastapi.testclient import TestClient

from app.main import create_app


def test_health_and_settings_endpoints():
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok"}
        assert client.get("/api/v1/health/ready").json()["database"] == "ok"
        settings = client.get("/api/v1/settings").json()
        assert settings["app_name"] == "PuzzleAI Employee"
        assert "database_url" not in settings
