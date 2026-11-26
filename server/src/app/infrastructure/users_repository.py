from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.entities import User
from app.domain.users_repository import EmailAlreadyExists
from app.infrastructure.models import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            password_hash=model.password_hash,
            created_at=model.created_at,
        )

    def get_by_email(self, email: str) -> User | None:
        model = self.session.scalar(select(UserModel).where(UserModel.email == email))
        return self._to_entity(model) if model is not None else None

    def get_by_id(self, user_id: int) -> User | None:
        model = self.session.get(UserModel, user_id)
        return self._to_entity(model) if model is not None else None

    def add(self, *, email: str, username: str, password_hash: str) -> User:
        model = UserModel(email=email, username=username, password_hash=password_hash)
        self.session.add(model)
        try:
            self.session.flush()
            user = self._to_entity(model)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            # Also catches concurrent registrations that passed the initial check.
            if self.get_by_email(email) is not None:
                raise EmailAlreadyExists() from exc
            raise
        except Exception:
            self.session.rollback()
            raise
        return user
