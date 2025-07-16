"""
Authentication Schemas
Pydantic models for auth-related requests and responses
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserCreate(BaseModel):
    """User registration request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    role: Optional[str] = "user"


class UserResponse(BaseModel):
    """User data response"""
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    is_verified: bool
    tenant_id: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePassword(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=8)


class EmailVerification(BaseModel):
    """Email verification request"""
    token: str


class ResendVerification(BaseModel):
    """Resend verification email request"""
    email: EmailStr


class LogoutRequest(BaseModel):
    """Logout request (for token blacklisting)"""
    token: Optional[str] = None


class AuthResponse(BaseModel):
    """Generic auth response"""
    message: str
    success: bool = True


class UserRegistrationResponse(BaseModel):
    """User registration response with additional info"""
    user: UserResponse
    message: str
    verification_required: bool = True