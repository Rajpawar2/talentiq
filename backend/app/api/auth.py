import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    RegisterResponse,
    UserLogin,
    UserResponse,
    Token
)
from app.auth.jwt import hash_password, verify_password, create_access_token
from app.auth.deps import get_current_user
from app.config import settings

logger = logging.getLogger("talentiq.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new user account.
    Account is immediately active and ready for login with no email OTP verification.
    """
    clean_email = payload.email.lower().strip()
    logger.info("[AUTH] Registration request received for: %s", clean_email)
    existing = db.query(User).filter(User.email == clean_email).first()

    if existing:
        logger.warning("[AUTH] Registration rejected: user already exists for %s", clean_email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    user = User(
        name=payload.name.strip(),
        email=clean_email,
        hashed_password=hash_password(payload.password),
        target_role=payload.target_role or "Software Engineer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("[AUTH] New user successfully registered: %s (id=%s)", clean_email, user.id)

    return RegisterResponse(
        success=True,
        message="User registered successfully.",
        email=user.email
    )


@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates user credentials and returns JWT access token.
    Allows immediate access to dashboard without email verification requirements.
    """
    clean_email = payload.email.lower().strip()
    logger.info("[AUTH] Login attempt for: %s", clean_email)
    user = db.query(User).filter(User.email == clean_email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        logger.warning("[AUTH] Login failed: invalid credentials for %s", clean_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    logger.info("[AUTH] User successfully logged in: %s (id=%s)", clean_email, user.id)

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieves the authenticated user's profile details."""
    return UserResponse.model_validate(current_user)
