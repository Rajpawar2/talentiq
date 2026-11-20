import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db, init_db, SessionLocal
from app.models.user import User
from app.auth.jwt import verify_password, decode_access_token
from app.services.email_service import email_service, MockEmailProvider


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()


@pytest.fixture
def client():
    email_service.provider = MockEmailProvider()
    email_service.provider.clear()
    return TestClient(app)


def test_1_new_user_can_register(client):
    """1. New user can register with name, email, password, and optional confirm_password."""
    email_service.provider.clear()
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"

    # Test registration with matching confirm_password
    res = client.post("/api/auth/register", json={
        "name": "Sarah Connor",
        "email": email,
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "target_role": "Cybersecurity Engineer"
    })

    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["message"] == "User registered successfully."
    assert data["email"] == email
    # Verify no OTP or verification email was dispatched
    assert len(email_service.provider.sent_messages) == 0

    # Test mismatched confirm_password rejection
    bad_email = f"bad_{uuid.uuid4().hex[:8]}@example.com"
    mismatch_res = client.post("/api/auth/register", json={
        "name": "Sarah Connor",
        "email": bad_email,
        "password": "SecurePassword123!",
        "confirm_password": "DifferentPassword123!",
        "target_role": "Cybersecurity Engineer"
    })
    assert mismatch_res.status_code == 422


def test_2_duplicate_email_registration_rejected(client):
    """2. Duplicate email registration is rejected with 400 Bad Request."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"

    # First registration
    res1 = client.post("/api/auth/register", json={
        "name": "Alice Smith",
        "email": email,
        "password": "Password123!",
        "target_role": "Frontend Developer"
    })
    assert res1.status_code == 201

    # Duplicate registration
    res2 = client.post("/api/auth/register", json={
        "name": "Alice Duplicate",
        "email": email,
        "password": "Password999!",
        "target_role": "Backend Developer"
    })
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


def test_3_password_is_securely_hashed(client):
    """3. Passwords are never stored in plain text and are securely hashed with bcrypt."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    plain_password = "MySuperSecretPassword#2026"

    res = client.post("/api/auth/register", json={
        "name": "Bob Stone",
        "email": email,
        "password": plain_password,
        "target_role": "Data Engineer"
    })
    assert res.status_code == 201

    # Verify directly from database
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        assert user.hashed_password != plain_password
        assert user.hashed_password.startswith("$2b$")  # Bcrypt hash identifier
        assert verify_password(plain_password, user.hashed_password) is True
        assert verify_password("WrongPassword!", user.hashed_password) is False
    finally:
        db.close()


def test_4_immediate_login_after_registration(client):
    """4. User can log in immediately after registration without any OTP or verification step."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    password = "InstantLogin123!"

    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "name": "Diana Prince",
        "email": email,
        "password": password,
        "target_role": "Staff Architect"
    })
    assert reg_res.status_code == 201

    # 2. Login immediately - NO OTP required!
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == email
    assert data["user"]["name"] == "Diana Prince"


def test_5_jwt_token_generated_correctly(client):
    """5. JWT token is generated correctly with valid subject and expiration."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    password = "JwtVerificationPass1!"

    client.post("/api/auth/register", json={
        "name": "Clark Kent",
        "email": email,
        "password": password
    })

    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["email"] == email
    assert "sub" in payload
    assert "exp" in payload
    assert "iat" in payload


def test_6_dashboard_loads_after_login(client):
    """6. Dashboard / authenticated user endpoints load successfully with the JWT token."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    password = "DashboardPass123!"

    client.post("/api/auth/register", json={
        "name": "Bruce Wayne",
        "email": email,
        "password": password
    })

    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch user profile
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == email
    assert user_data["name"] == "Bruce Wayne"

    # Fetch analytics overview for dashboard
    analytics_res = client.get("/api/analytics/overview", headers=headers)
    assert analytics_res.status_code == 200
    overview_data = analytics_res.json()
    assert "total_interviews" in overview_data


def test_7_protected_routes_require_authentication(client):
    """7. Protected routes reject requests with missing or invalid tokens (401 Unauthorized)."""
    # Missing token
    res_no_auth = client.get("/api/auth/me")
    assert res_no_auth.status_code == 401

    # Invalid / forged token
    res_bad_auth = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.fake.token"})
    assert res_bad_auth.status_code == 401


def test_8_existing_users_can_still_login(client):
    """8. Existing users in the database continue to log in without issues."""
    email = f"existing_{uuid.uuid4().hex[:8]}@example.com"
    password = "LegacyPassword123!"

    # Create user
    reg_res = client.post("/api/auth/register", json={
        "name": "Legacy User",
        "email": email,
        "password": password
    })
    assert reg_res.status_code == 201

    # Verify user can log in
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    assert login_res.json()["user"]["email"] == email


def test_9_logout_behavior(client):
    """9. Logout works cleanly by discarding token client-side."""
    email = f"candidate_{uuid.uuid4().hex[:8]}@example.com"
    password = "LogoutPass123!"

    client.post("/api/auth/register", json={
        "name": "Barry Allen",
        "email": email,
        "password": password
    })

    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    token = login_res.json()["access_token"]

    # Authenticated request succeeds
    auth_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert auth_res.status_code == 200

    # Simulating client discarding token on logout
    unauth_res = client.get("/api/auth/me", headers={})
    assert unauth_res.status_code == 401


def test_10_no_otp_endpoints_remain(client):
    """10. OTP-related endpoints have been completely removed and return 404 Not Found."""
    email = "test@example.com"

    # Verify /api/auth/verify-email is gone
    verify_res = client.post("/api/auth/verify-email", json={"email": email, "otp": "123456"})
    assert verify_res.status_code == 404

    # Verify /api/auth/resend-otp is gone
    resend_res = client.post("/api/auth/resend-otp", json={"email": email})
    assert resend_res.status_code == 404

    # Verify /api/auth/dev-mock-otp is gone
    dev_res = client.get(f"/api/auth/dev-mock-otp?email={email}")
    assert dev_res.status_code == 404
