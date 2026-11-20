from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirm_password: Optional[str] = None
    target_role: Optional[str] = "Software Engineer"

    @model_validator(mode="after")
    def validate_password_confirmation(self):
        if self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self

class RegisterResponse(BaseModel):
    success: bool = True
    message: str = "User registered successfully."
    email: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    target_role: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
