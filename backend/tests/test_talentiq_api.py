import uuid
import pytest
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

def create_and_authenticate_user(client, name="Alex Morgan", email=None, password="Password123!", target_role="Software Engineer") -> dict:
    """Helper to perform the complete register -> OTP verify -> login flow and return auth headers."""
    if not email:
        email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    
    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "name": name,
        "email": email,
        "password": password,
        "target_role": target_role
    })
    assert reg_res.status_code == 201

    # 2. Extract OTP from mock email
    latest_email = email_service.provider.sent_messages[-1]
    otp = latest_email["subject"].split()[0]

    # 3. Verify Email
    ver_res = client.post("/api/auth/verify-email", json={
        "email": email,
        "otp": otp
    })
    assert ver_res.status_code == 200

    # 4. Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    return {
        "access_token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"},
        "user": token_data["user"]
    }

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["ai_mock_mode"] is True

def test_auth_workflow(client):
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    
    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "name": "Alex Morgan",
        "email": email,
        "password": "SecurePassword123!",
        "target_role": "Senior AI Engineer"
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["success"] is True
    assert reg_data["email"] == email

    # 2. Extract OTP from mock email
    otp = email_service.provider.sent_messages[-1]["subject"].split()[0]
    assert len(otp) == 6

    # 3. Verify OTP
    verify_res = client.post("/api/auth/verify-email", json={
        "email": email,
        "otp": otp
    })
    assert verify_res.status_code == 200
    assert verify_res.json()["success"] is True

    # 4. Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["user"]["email"] == email
    assert token_data["user"]["email_verified"] is True

    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 5. Authenticate /me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["name"] == "Alex Morgan"

def test_resume_and_job_matching(client):
    auth = create_and_authenticate_user(client, name="Jordan Lee", target_role="Backend Engineer")
    headers = auth["headers"]

    # Create job description
    job_res = client.post("/api/jobs", json={
        "title": "Senior Backend Engineer",
        "company": "ScaleAI",
        "raw_text": "We are seeking a Senior Backend Engineer proficient in Python, FastAPI, PostgreSQL, Docker, and Redis microservices."
    }, headers=headers)
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # Test matching directly with text payload
    match_res = client.post("/api/matching/analyze", json={
        "job_id": job_id,
        "resume_text": "Jordan Lee. Experienced in Python, FastAPI, PostgreSQL, and REST APIs with 4 years experience."
    }, headers=headers)
    assert match_res.status_code == 200
    match_data = match_res.json()
    assert match_data["match_score"] > 40
    assert "Python" in match_data["matched_skills"] or "FastAPI" in match_data["matched_skills"]

def test_full_interview_lifecycle(client):
    auth = create_and_authenticate_user(client, name="Taylor Swift")
    headers = auth["headers"]

    # 1. Create Interview
    intv_res = client.post("/api/interviews", json={
        "role": "Full-Stack AI Developer",
        "interview_type": "Technical",
        "difficulty": "Medium",
        "total_questions": 3,
        "duration_minutes": 20
    }, headers=headers)
    assert intv_res.status_code == 201
    intv_data = intv_res.json()
    assert len(intv_data["questions"]) == 3
    interview_id = intv_data["id"]
    first_q_id = intv_data["questions"][0]["id"]

    # 2. Start Interview
    start_res = client.post(f"/api/interviews/{interview_id}/start", headers=headers)
    assert start_res.status_code == 200
    assert start_res.json()["status"] == "in_progress"

    # 3. Submit Answer with filler words
    answer_res = client.post(f"/api/interviews/{interview_id}/answer", json={
        "question_id": first_q_id,
        "answer_text": "Um, in our architecture, basically we used FastAPI for asynchronous processing and Redis for caching, you know.",
        "input_mode": "text",
        "audio_duration_seconds": 15.0
    }, headers=headers)
    assert answer_res.status_code == 200
    ans_data = answer_res.json()
    assert ans_data["filler_words_count"] >= 2
    assert "clarity_indicator" in ans_data["communication_indicators"]

    # 4. Check intermediate report or complete
    comp_res = client.post(f"/api/interviews/{interview_id}/complete", headers=headers)
    assert comp_res.status_code == 200

    # 5. Fetch Final Report
    report_res = client.get(f"/api/interviews/{interview_id}/report", headers=headers)
    assert report_res.status_code == 200
    rep = report_res.json()
    assert rep["overall_score"] > 0
    assert len(rep["question_reviews"]) >= 1
    assert "interview_readiness" in rep

def test_analytics(client):
    auth = create_and_authenticate_user(client, name="Sam Altman")
    headers = auth["headers"]

    overview = client.get("/api/analytics/overview", headers=headers)
    assert overview.status_code == 200
    assert "average_score" in overview.json()

    progress = client.get("/api/analytics/progress", headers=headers)
    assert progress.status_code == 200
    assert len(progress.json()["skill_radar"]) > 0

def test_resume_upload_pdf(client):
    """Test 1: Valid PDF upload under 10MB."""
    auth = create_and_authenticate_user(client, name="Alex Morgan")
    headers = auth["headers"]

    with open("tests/sample_resume.pdf", "rb") as f:
        pdf_bytes = f.read()

    res = client.post(
        "/api/resumes/upload",
        files={"file": ("sample_resume.pdf", pdf_bytes, "application/pdf")},
        headers=headers
    )
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["parsed"] is True
    assert data["filename"] == "sample_resume.pdf"
    assert data["file_type"] == "pdf"
    assert "resume_id" in data
    assert len(data["skills"]) > 0
    assert "name" in data["parsed_data"]

def test_resume_upload_docx(client):
    """Test 2: Valid DOCX upload under 10MB."""
    auth = create_and_authenticate_user(client, name="Morgan Stanley")
    headers = auth["headers"]

    with open("tests/sample_resume.docx", "rb") as f:
        docx_bytes = f.read()

    res = client.post(
        "/api/resumes/upload",
        files={"file": ("sample_resume.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers=headers
    )
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["parsed"] is True
    assert data["filename"] == "sample_resume.docx"
    assert data["file_type"] == "docx"
    assert "resume_id" in data
    assert len(data["skills"]) > 0

def test_resume_upload_unsupported_txt(client):
    """Test 3: TXT file rejected with 400 Bad Request."""
    auth = create_and_authenticate_user(client, name="Bob Smith")
    headers = auth["headers"]

    res = client.post(
        "/api/resumes/upload",
        files={"file": ("resume.txt", b"plain text resume", "text/plain")},
        headers=headers
    )
    assert res.status_code == 400
    assert "unsupported" in res.json()["detail"].lower()

def test_resume_upload_oversized(client):
    """Test 4: Oversized file rejected with 413 Payload Too Large."""
    auth = create_and_authenticate_user(client, name="Big Data")
    headers = auth["headers"]

    # 11MB file payload
    fake_huge_bytes = b"%PDF-1.4\n" + b"0" * (11 * 1024 * 1024)

    res = client.post(
        "/api/resumes/upload",
        files={"file": ("huge_resume.pdf", fake_huge_bytes, "application/pdf")},
        headers=headers
    )
    assert res.status_code == 413
    assert "exceeds" in res.json()["detail"].lower()

def test_resume_upload_unauthenticated(client):
    """Test 5: Upload without token rejected with 401 Unauthorized."""
    with open("tests/sample_resume.pdf", "rb") as f:
        pdf_bytes = f.read()

    res = client.post(
        "/api/resumes/upload",
        files={"file": ("sample_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert res.status_code == 401
