from ascender.core.database import DBEntity
from sqlalchemy.orm import Mapped, mapped_column


class UserEntity(DBEntity):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()