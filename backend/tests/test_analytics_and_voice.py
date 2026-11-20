import uuid
import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.services.email_service import email_service, MockEmailProvider

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()

@pytest.fixture
def client():
    email_service.provider = MockEmailProvider()
    return TestClient(app)

def create_fresh_authenticated_user(client) -> dict:
    email = f"zero_user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg = client.post("/api/auth/register", json={
        "name": "Zero State User",
        "email": email,
        "password": pwd,
        "target_role": "Backend Engineer"
    })
    assert reg.status_code == 201

    login = client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"token": token, "headers": {"Authorization": f"Bearer {token}"}, "email": email}


# ==========================================================
# 1. ZERO-STATE ANALYTICS INTEGRITY TESTS
# ==========================================================

def test_analytics_overview_zero_state(client):
    """A new user with zero completed mock interviews must receive honest 0.0 metrics and an empty trend list (no fake demo-1, demo-2, demo-3)."""
    user = create_fresh_authenticated_user(client)
    res = client.get("/api/analytics/overview", headers=user["headers"])
    assert res.status_code == 200
    data = res.json()

    assert data["total_interviews"] == 0
    assert data["average_score"] == 0.0
    assert data["best_score"] == 0.0
    assert data["technical_score"] == 0.0
    assert data["communication_score"] == 0.0
    # Trend MUST be empty for a new user, NEVER fake demo points!
    assert data["performance_trend"] == []
    # No fake strengths or gaps fabricated
    assert data["skill_strengths"] == []
    assert data["skill_gaps"] == []


def test_analytics_progress_zero_state(client):
    """Progress curves and radar metrics for a user with zero reports must return honest baseline zeros, not fake history."""
    user = create_fresh_authenticated_user(client)
    res = client.get("/api/analytics/progress", headers=user["headers"])
    assert res.status_code == 200
    data = res.json()

    assert data["score_over_time"] == []
    assert data["category_averages"]["technical"] == 0.0
    assert data["category_averages"]["communication"] == 0.0
    assert data["category_averages"]["problem_solving"] == 0.0
    assert data["category_averages"]["behavioral"] == 0.0


# ==========================================================
# 2. VOICE & AUDIO VALIDATION TESTS
# ==========================================================

def test_voice_transcribe_unsupported_format(client):
    user = create_fresh_authenticated_user(client)
    fake_exe = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00")
    files = {"audio": ("malicious.exe", fake_exe, "application/octet-stream")}
    
    res = client.post("/api/voice/transcribe", files=files, headers=user["headers"])
    assert res.status_code == 400
    assert "unsupported audio format" in res.json()["detail"].lower()


def test_voice_transcribe_empty_audio(client):
    user = create_fresh_authenticated_user(client)
    empty_bytes = io.BytesIO(b"")
    files = {"audio": ("silence.webm", empty_bytes, "audio/webm")}
    
    res = client.post("/api/voice/transcribe", files=files, headers=user["headers"])
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["transcript"] == ""
