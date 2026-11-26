from dataclasses import dataclass, field

from app.application.security import InvalidAccessToken, PasswordHasher, TokenHandler
from app.domain.entities import User
from app.domain.users_repository import EmailAlreadyExists, UserRepository


class InvalidCredentials(Exception):
    """The supplied email or password is incorrect."""


@dataclass(frozen=True)
class AuthenticationResult:
    user: User
    access_token: str = field(repr=False)


class AuthenticationService:
    def __init__(
        self,
        users_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_handler: TokenHandler,
    ):
        self.users_repository = users_repository
        self.password_hasher = password_hasher
        self.token_handler = token_handler

    def register(self, *, email: str, password: str, username: str) -> AuthenticationResult:
        email = email.strip().lower()
        if self.users_repository.get_by_email(email) is not None:
            raise EmailAlreadyExists()
        user = self.users_repository.add(
            email=email,
            username=username,
            password_hash=self.password_hasher.hash(password),
        )
        return AuthenticationResult(user, self.token_handler.create_access_token(user.id))

    def login(self, *, email: str, password: str) -> AuthenticationResult:
        user = self.users_repository.get_by_email(email.strip().lower())
        if user is None:
            self.password_hasher.verify_dummy(password)
            raise InvalidCredentials()
        if not self.password_hasher.verify(password, user.password_hash):
            raise InvalidCredentials()
        return AuthenticationResult(user, self.token_handler.create_access_token(user.id))

    def authenticate(self, token: str) -> User:
        user_id = self.token_handler.get_user_id(token)
        user = self.users_repository.get_by_id(user_id)
        if user is None:
            raise InvalidAccessToken()
        return user
