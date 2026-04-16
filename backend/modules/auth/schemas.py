from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class RequestOTP(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    is_verified: bool
    created_at: datetime
