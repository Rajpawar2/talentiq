from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    RegisterResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
    ResendOTPRequest,
    ResendOTPResponse,
    UserLogin,
    UserResponse,
    Token
)
from app.auth.jwt import hash_password, verify_password, create_access_token
from app.auth.deps import get_current_user
from app.config import settings
from app.utils.otp import generate_secure_otp, hash_otp, verify_otp_hash
from app.services.email_service import email_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new user account with pending email verification.
    Generates a secure 6-digit OTP and delivers it to the user's email address.
    """
    clean_email = payload.email.lower().strip()
    existing = db.query(User).filter(User.email == clean_email).first()

    if existing:
        if existing.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists."
            )
        
        # User exists but is unverified (previous registration did not complete)
        # Check resend cooldown
        if existing.last_otp_sent_at:
            elapsed = (datetime.utcnow() - existing.last_otp_sent_at).total_seconds()
            if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
                wait_sec = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Please wait {wait_sec} seconds before requesting a new OTP."
                )

        otp = generate_secure_otp()
        existing.name = payload.name.strip()
        existing.hashed_password = hash_password(payload.password)
        existing.target_role = payload.target_role or "Software Engineer"
        existing.verification_otp_hash = hash_otp(otp)
        existing.verification_otp_expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        existing.verification_attempts = 0
        existing.last_otp_sent_at = datetime.utcnow()
        db.commit()

        try:
            email_service.send_verification_otp(existing.email, existing.name, otp)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to send verification email. Please try again."
            )

        return RegisterResponse(
            success=True,
            message="Verification email sent successfully.",
            email=existing.email
        )

    # New user creation
    otp = generate_secure_otp()
    user = User(
        name=payload.name.strip(),
        email=clean_email,
        hashed_password=hash_password(payload.password),
        target_role=payload.target_role or "Software Engineer",
        email_verified=False,
        verification_otp_hash=hash_otp(otp),
        verification_otp_expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        verification_attempts=0,
        last_otp_sent_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    try:
        email_service.send_verification_otp(user.email, user.name, otp)
    except Exception:
        db.delete(user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to send verification email. Please try again."
        )

    return RegisterResponse(
        success=True,
        message="Verification email sent successfully.",
        email=user.email
    )


@router.post("/verify-email", response_model=VerifyEmailResponse, status_code=status.HTTP_200_OK)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    """
    Validates the 6-digit OTP and marks the user's email as verified.
    Guards against brute-force (max 5 attempts) and expired OTPs (10 min).
    """
    clean_email = payload.email.lower().strip()
    clean_otp = payload.otp.strip()

    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No account found with this email."
        )

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified."
        )

    if not user.verification_otp_hash or not user.verification_otp_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending verification code found. Please request a new OTP."
        )

    # Check maximum attempt limit
    if user.verification_attempts >= settings.OTP_MAX_ATTEMPTS:
        user.verification_otp_hash = None
        user.verification_otp_expires_at = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum verification attempts exceeded. Please request a new OTP."
        )

    # Check expiration
    if datetime.utcnow() > user.verification_otp_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new OTP."
        )

    # Validate OTP hash
    if not verify_otp_hash(clean_otp, user.verification_otp_hash):
        user.verification_attempts += 1
        attempts_left = max(0, settings.OTP_MAX_ATTEMPTS - user.verification_attempts)
        
        if user.verification_attempts >= settings.OTP_MAX_ATTEMPTS:
            user.verification_otp_hash = None
            user.verification_otp_expires_at = None
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum verification attempts exceeded. Please request a new OTP."
            )
        
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {attempts_left} attempt(s) remaining."
        )

    # Verification successful
    user.email_verified = True
    user.verification_otp_hash = None
    user.verification_otp_expires_at = None
    user.verification_attempts = 0
    db.commit()
    db.refresh(user)

    return VerifyEmailResponse(
        success=True,
        message="Email verified successfully"
    )


@router.post("/resend-otp", response_model=ResendOTPResponse, status_code=status.HTTP_200_OK)
def resend_otp(payload: ResendOTPRequest, db: Session = Depends(get_db)):
    """
    Regenerates and resends a 6-digit OTP. Enforces a 60-second cooldown period.
    """
    clean_email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == clean_email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No account found with this email."
        )

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified."
        )

    # Enforce resend cooldown
    if user.last_otp_sent_at:
        elapsed = (datetime.utcnow() - user.last_otp_sent_at).total_seconds()
        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            wait_sec = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {wait_sec} seconds before requesting a new OTP."
            )

    # Invalidate old OTP and generate fresh one
    otp = generate_secure_otp()
    user.verification_otp_hash = hash_otp(otp)
    user.verification_otp_expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    user.verification_attempts = 0
    user.last_otp_sent_at = datetime.utcnow()
    db.commit()

    try:
        email_service.send_verification_otp(user.email, user.name, otp)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to send verification email. Please try again."
        )

    return ResendOTPResponse(
        success=True,
        message="A new verification code has been sent to your email.",
        cooldown_seconds=settings.OTP_RESEND_COOLDOWN_SECONDS
    )


@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates user credentials and returns JWT access token.
    Blocks login for accounts where email_verified is False.
    """
    clean_email = payload.email.lower().strip()
    user = db.query(User).filter(User.email == clean_email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Check email verification status
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email before logging in."
        )

    token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieves the authenticated user's profile details."""
    return UserResponse.model_validate(current_user)
