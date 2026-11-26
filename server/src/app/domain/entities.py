from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: int
    email: str
    username: str
    password_hash: str = field(repr=False)
    created_at: datetime
