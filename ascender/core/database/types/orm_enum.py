from enum import Enum


class ORMEnum(Enum):
    TORTOISE = "tortoise"
    """Tortoise ORM"""
    SQLALCHEMY = "sqlalchemy"
    """SQLAlchemy ORM"""