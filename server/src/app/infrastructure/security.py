from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.application.security import InvalidAccessToken


class Argon2PasswordHasher:
    def __init__(self):
        self._hasher = PasswordHash.recommended()
        self._dummy_hash = self._hasher.hash("dummy-password-for-timing")

    def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        return self._hasher.verify(password, password_hash)

    def verify_dummy(self, password: str) -> None:
        self._hasher.verify(password, self._dummy_hash)


class JwtTokenHandler:
    def __init__(self, secret_key: str):
        if len(secret_key.encode()) < 32:
            raise ValueError("JWT_SECRET_KEY must contain at least 32 bytes.")
        self._secret_key = secret_key

    def create_access_token(self, user_id: int) -> str:
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=15)},
            self._secret_key,
            algorithm="HS256",
        )

    def get_user_id(self, token: str) -> int:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=["HS256"],
                options={"require": ["sub", "iat", "exp"]},
            )
            subject = payload["sub"]
            if not isinstance(subject, str) or not subject.isascii() or not subject.isdigit():
                raise InvalidAccessToken()
            user_id = int(subject)
            if user_id < 1 or user_id > 2147483647:
                raise InvalidAccessToken()
            return user_id
        except (jwt.InvalidTokenError, ValueError) as exc:
            raise InvalidAccessToken() from exc
