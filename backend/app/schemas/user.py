from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    target_role: Optional[str] = "Software Engineer"

class RegisterResponse(BaseModel):
    success: bool = True
    message: str = "Verification email sent successfully."
    email: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

class VerifyEmailResponse(BaseModel):
    success: bool = True
    message: str = "Email verified successfully"

class ResendOTPRequest(BaseModel):
    email: EmailStr

class ResendOTPResponse(BaseModel):
    success: bool = True
    message: str = "Verification code resent successfully."
    cooldown_seconds: int = 60

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    target_role: Optional[str]
    email_verified: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
