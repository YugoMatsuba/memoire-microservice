from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.authentication import (
    AuthenticationResult,
    AuthenticationService,
    InvalidCredentials,
)
from app.domain.entities import User
from app.domain.users_repository import EmailAlreadyExists
from app.presentation.dependencies import get_authentication_service, get_current_user
from app.presentation.schemas.auth import (
    AuthenticationResponse,
    ErrorResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
AuthService = Annotated[AuthenticationService, Depends(get_authentication_service)]


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at,
    )


def _authentication_response(result: AuthenticationResult) -> AuthenticationResponse:
    return AuthenticationResponse(
        user=_user_response(result.user), access_token=result.access_token
    )


@router.post(
    "/register",
    response_model=AuthenticationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse, "description": "Email already registered"}},
)
def register(request: RegisterRequest, service: AuthService) -> AuthenticationResponse:
    try:
        result = service.register(
            email=str(request.email),
            password=request.password.get_secret_value(),
            username=request.username,
        )
    except EmailAlreadyExists as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        ) from exc
    return _authentication_response(result)


@router.post(
    "/login",
    response_model=AuthenticationResponse,
    responses={401: {"model": ErrorResponse, "description": "Invalid credentials"}},
)
def login(request: LoginRequest, service: AuthService) -> AuthenticationResponse:
    try:
        result = service.login(
            email=str(request.email), password=request.password.get_secret_value()
        )
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return _authentication_response(result)


@router.get(
    "/me",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse, "description": "Invalid access token"}},
)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return _user_response(current_user)
