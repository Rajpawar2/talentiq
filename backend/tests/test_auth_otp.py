import uuid
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.database import get_db, init_db
from app.models.user import User
from app.services.email_service import email_service, MockEmailProvider

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()

@pytest.fixture
def client():
    # Ensure email service uses MockEmailProvider
    email_service.provider = MockEmailProvider()
    return TestClient(app)

def get_latest_otp_from_email() -> str:
    """Helper to extract OTP from the latest mock email."""
    assert len(email_service.provider.sent_messages) > 0
    latest = email_service.provider.sent_messages[-1]
    # Subject format: f"{otp} is your TalentIQ verification code"
    otp = latest["subject"].split()[0]
    assert len(otp) == 6 and otp.isdigit()
    return otp


def test_1_successful_registration(client):
    """1. Successful registration creates unverified account and sends OTP."""
    email_service.provider.clear()
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"

    res = client.post("/api/auth/register", json={
        "name": "Sarah Connor",
        "email": email,
        "password": "Password123!",
        "target_role": "Cybersecurity Engineer"
    })

    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["email"] == email
    # Ensure OTP is NEVER exposed in the API response
    assert "otp" not in data
    assert "access_token" not in data


def test_2_registration_with_existing_email(client):
    """2. Registration with an existing verified email is rejected with 400."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"

    # Register and verify
    client.post("/api/auth/register", json={
        "name": "Sarah Connor",
        "email": email,
        "password": "Password123!"
    })
    otp = get_latest_otp_from_email()
    client.post("/api/auth/verify-email", json={"email": email, "otp": otp})

    # Try registering again
    res = client.post("/api/auth/register", json={
        "name": "Sarah Connor",
        "email": email,
        "password": "NewPassword123!"
    })
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"].lower()


def test_3_otp_email_generation(client):
    """3. Verification email is properly formatted and contains 6-digit OTP."""
    email_service.provider.clear()
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"

    client.post("/api/auth/register", json={
        "name": "John Doe",
        "email": email,
        "password": "Password123!"
    })

    assert len(email_service.provider.sent_messages) == 1
    sent = email_service.provider.sent_messages[0]
    assert sent["to"] == email
    otp = sent["subject"].split()[0]
    assert len(otp) == 6 and otp.isdigit()
    assert "TalentIQ" in sent["html_body"]
    assert otp in sent["html_body"]
    assert "expires in" in sent["html_body"].lower()
    assert f"{otp}" in sent["text_body"]
    assert "expires in 10 minutes" in sent["text_body"].lower()


def test_4_correct_otp_verification(client):
    """4. Correct OTP marks email as verified and cleans up OTP hash."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Ada Lovelace",
        "email": email,
        "password": "Password123!"
    })
    otp = get_latest_otp_from_email()

    res = client.post("/api/auth/verify-email", json={
        "email": email,
        "otp": otp
    })
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Check database state
    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    assert user.email_verified is True
    assert user.verification_otp_hash is None
    assert user.verification_otp_expires_at is None
    assert user.verification_attempts == 0
    db.close()


def test_5_incorrect_otp(client):
    """5. Incorrect OTP returns 400 with remaining attempts counter."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Grace Hopper",
        "email": email,
        "password": "Password123!"
    })

    res = client.post("/api/auth/verify-email", json={
        "email": email,
        "otp": "000000"
    })
    assert res.status_code == 400
    assert "invalid otp" in res.json()["detail"].lower()
    assert "4 attempt(s) remaining" in res.json()["detail"]


def test_6_expired_otp(client):
    """6. Expired OTP is rejected with clear expiration message."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Alan Turing",
        "email": email,
        "password": "Password123!"
    })
    otp = get_latest_otp_from_email()

    # Expire OTP in database
    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    user.verification_otp_expires_at = datetime.utcnow() - timedelta(minutes=1)
    db.commit()
    db.close()

    res = client.post("/api/auth/verify-email", json={
        "email": email,
        "otp": otp
    })
    assert res.status_code == 400
    assert "otp has expired" in res.json()["detail"].lower()


def test_7_five_failed_attempts(client):
    """7. Five failed attempts invalidates OTP and locks verification."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Claude Shannon",
        "email": email,
        "password": "Password123!"
    })
    real_otp = get_latest_otp_from_email()

    # Submit 4 wrong attempts
    for i in range(4):
        res = client.post("/api/auth/verify-email", json={
            "email": email,
            "otp": "111111"
        })
        assert res.status_code == 400

    # 5th wrong attempt triggers invalidation
    res_5th = client.post("/api/auth/verify-email", json={
        "email": email,
        "otp": "111111"
    })
    assert res_5th.status_code == 400
    assert "maximum verification attempts exceeded" in res_5th.json()["detail"].lower()

    # Even the correct OTP fails now because it was invalidated
    res_6th = client.post("/api/auth/verify-email", json={
        "email": email,
        "otp": real_otp
    })
    assert res_6th.status_code == 400


def test_8_otp_resend(client):
    """8. User can request a new OTP after cooldown."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Margaret Hamilton",
        "email": email,
        "password": "Password123!"
    })

    # Fast-forward last_otp_sent_at past 60s cooldown
    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    user.last_otp_sent_at = datetime.utcnow() - timedelta(seconds=65)
    db.commit()
    db.close()

    email_service.provider.clear()
    res = client.post("/api/auth/resend-otp", json={"email": email})
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert len(email_service.provider.sent_messages) == 1


def test_9_resend_cooldown(client):
    """9. Resend OTP within cooldown period returns 429 Too Many Requests."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Tim Berners-Lee",
        "email": email,
        "password": "Password123!"
    })

    # Immediate resend without waiting
    res = client.post("/api/auth/resend-otp", json={"email": email})
    assert res.status_code == 429
    assert "wait" in res.json()["detail"].lower()


def test_10_old_otp_invalidation(client):
    """10. Requesting a new OTP invalidates the previous OTP."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Linus Torvalds",
        "email": email,
        "password": "Password123!"
    })
    otp1 = get_latest_otp_from_email()

    # Bypass cooldown
    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    user.last_otp_sent_at = datetime.utcnow() - timedelta(seconds=65)
    db.commit()
    db.close()

    client.post("/api/auth/resend-otp", json={"email": email})
    otp2 = get_latest_otp_from_email()
    assert otp1 != otp2

    # Attempt to verify using old OTP
    res_old = client.post("/api/auth/verify-email", json={"email": email, "otp": otp1})
    assert res_old.status_code == 400

    # Verify using new OTP
    res_new = client.post("/api/auth/verify-email", json={"email": email, "otp": otp2})
    assert res_new.status_code == 200
    assert res_new.json()["success"] is True


def test_11_successful_email_verification_prevents_duplicate_verify(client):
    """11. Verified email cannot be verified again."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Barbara Liskov",
        "email": email,
        "password": "Password123!"
    })
    otp = get_latest_otp_from_email()

    res1 = client.post("/api/auth/verify-email", json={"email": email, "otp": otp})
    assert res1.status_code == 200

    res2 = client.post("/api/auth/verify-email", json={"email": email, "otp": otp})
    assert res2.status_code == 400
    assert "already verified" in res2.json()["detail"].lower()


def test_12_login_before_verification(client):
    """12. Login is blocked before email verification."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Ken Thompson",
        "email": email,
        "password": "Password123!"
    })

    res = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    assert res.status_code == 401
    assert "please verify your email" in res.json()["detail"].lower()


def test_13_login_after_verification(client):
    """13. Login succeeds after verification and returns valid JWT access token."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Dennis Ritchie",
        "email": email,
        "password": "Password123!"
    })
    otp = get_latest_otp_from_email()
    client.post("/api/auth/verify-email", json={"email": email, "otp": otp})

    res = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == email
    assert data["user"]["email_verified"] is True

    # Also test authenticated protected route /api/auth/me
    token = data["access_token"]
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["name"] == "Dennis Ritchie"


def test_14_email_service_failure(client):
    """14. Email service failure during registration aborts transaction and returns 500."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"

    with patch.object(email_service, "send_verification_otp", side_effect=Exception("SMTP Down")):
        res = client.post("/api/auth/register", json={
            "name": "Guido van Rossum",
            "email": email,
            "password": "Password123!"
        })
        assert res.status_code == 500
        assert "unable to send verification email" in res.json()["detail"].lower()

    # User row should be rolled back / deleted so user can try again
    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    assert user is None
    db.close()


def test_15_rate_limiting_rapid_resends(client):
    """15. Multiple rapid OTP resend requests are rejected by rate limit."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "name": "Bjarne Stroustrup",
        "email": email,
        "password": "Password123!"
    })

    # Rapid resend attempts
    for _ in range(3):
        res = client.post("/api/auth/resend-otp", json={"email": email})
        assert res.status_code == 429
        assert "wait" in res.json()["detail"].lower()
