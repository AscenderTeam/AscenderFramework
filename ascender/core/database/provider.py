from typing import Any, Sequence
from ascender.core.database.engine import DatabaseEngine
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.core.database.types.sqlalchemy_configuration import SQLAlchemyConfig
from ascender.core.di.interface.provider import Provider


def provideDatabase(orm_mode: ORMEnum, orm_configuration: Any) -> Provider | Sequence[Provider]:
    """
    Provides the DatabaseEngine based on the ORM mode.

    Usage example:
    ```python
    # src/bootstrap.py
    
    from ascender.core.database import provideDatabase, ORMEnum
    
    providers = [
        provideDatabase(ORMEnum.SQLALCHEMY, {
            "database_url": "sqlite+aiosqlite:///./test.db",
            "entities": [...], # specify path using python's import style path (e.g. "entities.users")
        }),
    ]
    ```
    
    Args:
        orm_mode (ORMEnum): The ORM mode to use.
        orm_configuration (Any): The configuration for the ORM.

    Returns:
        Provider | Sequence[Provider]: The provider for the DatabaseEngine.
    """
    if orm_mode == ORMEnum.TORTOISE:
        return {
            "provide": DatabaseEngine,
            "value": DatabaseEngine(orm_mode, orm_configuration),
        }
    
    if orm_mode == ORMEnum.SQLALCHEMY:
        return [
            {
                "provide": DatabaseEngine,
                "value": sqlalchemy_factory(orm_configuration),
            }
        ]


def sqlalchemy_factory(configuration: SQLAlchemyConfig):
    database = DatabaseEngine(ORMEnum.SQLALCHEMY, configuration)
    database.load_entity(*configuration['entities'])

    return database