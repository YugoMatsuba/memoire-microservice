from typing import Protocol


class InvalidAccessToken(Exception):
    """The access token is invalid or expired."""


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, password_hash: str) -> bool: ...

    def verify_dummy(self, password: str) -> None: ...


class TokenHandler(Protocol):
    def create_access_token(self, user_id: int) -> str: ...

    def get_user_id(self, token: str) -> int: ...
