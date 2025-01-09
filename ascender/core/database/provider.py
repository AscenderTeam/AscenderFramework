from typing import Sequence
from ascender.core.applications.application import Application
from ascender.core.database.engine import DatabaseEngine
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.core.database.types.sqlalchemy_configuration import SQLAlchemyConfig
from ascender.core.database.types.tortoise_configuration import TortoiseConfig
from ascender.core.di.interface.provider import Provider
from ascender.core.registries.service import ServiceRegistry


def provideDatabase(orm_mode: ORMEnum, orm_configuration: TortoiseConfig | SQLAlchemyConfig) -> Provider | Sequence[Provider]:
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