from sqlalchemy.orm import Mapped, mapped_column

from ascender.core.database import DBEntity


class UserEntity(DBEntity):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
