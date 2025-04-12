from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.mixins.int_user_pk import IntPkMixin


class User(Base, IntPkMixin):
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    password: Mapped[str]
