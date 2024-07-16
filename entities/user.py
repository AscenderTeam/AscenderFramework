from core.database.entity import DBEntity
from sqlalchemy import Column, Integer, String, Text


class UserEntity(DBEntity):
    __tablename__ = "user"

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(60), index=True)
    email: str | None = Column(String(60), nullable=True)
    password: str = Column(Text)