from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field, SecretStr, StringConstraints


class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=320)
    password: SecretStr = Field(min_length=1)


class RegisterRequest(BaseModel):
    email: EmailStr = Field(max_length=320)
    password: SecretStr = Field(min_length=16)
    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)
    ]


class UserResponse(BaseModel):
    """Public user fields; credentials must never be returned."""

    id: int
    email: EmailStr
    username: str
    created_at: datetime


class ErrorResponse(BaseModel):
    detail: str


class AuthenticationResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: Literal["bearer"] = "bearer"
