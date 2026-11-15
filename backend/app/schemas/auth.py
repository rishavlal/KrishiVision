"""
Auth Schemas for KrishiVision
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100, description="Valid email address")
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = Field(default=None, max_length=100)
    farm_location: Optional[str] = Field(default="Jharkhand, India", max_length=100)
    farm_size_hectares: Optional[float] = Field(default=2.5, ge=0.1, le=1000.0)
    phone_number: Optional[str] = Field(default=None, max_length=20)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=100)
    farm_location: Optional[str] = Field(default=None, max_length=100)
    farm_size_hectares: Optional[float] = Field(default=None, ge=0.1, le=1000.0, description="Farm size in hectares (0.1 to 1000.0)")
    phone_number: Optional[str] = Field(default=None, max_length=20)


class UserLogin(BaseModel):
    username: str = Field(..., description="Username or email address")
    password: str = Field(...)


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    farm_location: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    phone_number: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
