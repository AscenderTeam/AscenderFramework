from sqlalchemy import Integer, String
from ascender.core.database.entity import DBEntity
from sqlalchemy.orm import Mapped, mapped_column


class TestEntity(DBEntity):
    __tablename__ = "tests"
    
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    name: Mapped[str] = mapped_column(String())