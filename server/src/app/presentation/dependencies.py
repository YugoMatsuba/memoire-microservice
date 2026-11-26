import os
from collections.abc import Iterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.authentication import AuthenticationService
from app.application.security import InvalidAccessToken
from app.domain.entities import User
from app.infrastructure.database import get_session_factory
from app.infrastructure.security import Argon2PasswordHasher, JwtTokenHandler
from app.infrastructure.users_repository import SqlAlchemyUserRepository


def get_session() -> Iterator[Session]:
    with get_session_factory()() as session:
        yield session


@lru_cache
def get_password_hasher() -> Argon2PasswordHasher:
    return Argon2PasswordHasher()


@lru_cache
def get_token_handler() -> JwtTokenHandler:
    return JwtTokenHandler(os.environ["JWT_SECRET_KEY"])


def get_authentication_service(
    session: Annotated[Session, Depends(get_session)],
    hasher: Annotated[Argon2PasswordHasher, Depends(get_password_hasher)],
    tokens: Annotated[JwtTokenHandler, Depends(get_token_handler)],
) -> AuthenticationService:
    return AuthenticationService(SqlAlchemyUserRepository(session), hasher, tokens)


bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> User:
    if credentials is not None:
        try:
            return service.authenticate(credentials.credentials)
        except InvalidAccessToken:
            pass
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
