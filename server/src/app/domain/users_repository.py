from typing import Protocol

from app.domain.entities import User


class EmailAlreadyExists(Exception):
    """A user with this email already exists."""


class UserRepository(Protocol):
    def get_by_email(self, email: str) -> User | None: ...

    def get_by_id(self, user_id: int) -> User | None: ...

    def add(self, *, email: str, username: str, password_hash: str) -> User:
        """Persist and commit a new user, or raise EmailAlreadyExists."""
        ...
