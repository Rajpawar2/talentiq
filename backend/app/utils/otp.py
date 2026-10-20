import hmac
import hashlib
import secrets
from app.config import settings

def generate_secure_otp() -> str:
    """Generates a cryptographically secure random 6-digit numeric OTP."""
    # secrets.randbelow(1_000_000) returns 0 to 999999 inclusive
    random_int = secrets.randbelow(1_000_000)
    return f"{random_int:06d}"

def hash_otp(otp: str) -> str:
    """Hashes a 6-digit OTP using HMAC-SHA256 with JWT_SECRET as key."""
    clean_otp = otp.strip()
    return hmac.new(
        settings.JWT_SECRET.encode("utf-8"),
        clean_otp.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def verify_otp_hash(otp: str, stored_hash: str) -> bool:
    """
    Constant-time verification of raw OTP against the stored HMAC hash.
    Protects against timing attacks.
    """
    if not stored_hash or not otp:
        return False
    computed_hash = hash_otp(otp)
    return hmac.compare_digest(computed_hash, stored_hash)
