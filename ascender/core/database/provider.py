from ascender.abstracts.factory import AbstractFactory
from ascender.abstracts.module import AbstractModule
from ascender.core.application import Application
from ascender.core.database.engine import DatabaseEngine
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.core.database.types.sqlalchemy_configuration import SQLAlchemyConfig
from ascender.core.database.types.tortoise_configuration import TortoiseConfig
from ascender.core.registries.service import ServiceRegistry


class DatabaseProvider(AbstractModule, AbstractFactory):
    def __init__(
        self,
        orm_mode: ORMEnum,
        orm_configuration: TortoiseConfig | SQLAlchemyConfig,
    ):
        self.orm_mode = orm_mode
        self.orm_configuration = orm_configuration
    
    def on_application_bootstrap(self, application: Application):
        
        if self.orm_mode == ORMEnum.TORTOISE:
            db = self.withTortoise(self.orm_configuration)
        
        if self.orm_mode == ORMEnum.SQLALCHEMY:
            db = self.withSQLAlchemy(self.orm_configuration)
        
        self.factory_add(DatabaseEngine, db)

    def withTortoise(
        self,
        configuration: TortoiseConfig,
    ):
        service_registry = ServiceRegistry()
        if not (application := service_registry.resolve(Application)):
            return
        
        database = DatabaseEngine(application.app, 
                                  ORMEnum.TORTOISE,
                                  configuration)
        database.run_database()
        return database

    def withSQLAlchemy(
        self,
        configuration: SQLAlchemyConfig,
    ):
        service_registry = ServiceRegistry()
        if not (application := service_registry.resolve(Application)):
            return
        
        database = DatabaseEngine(application.app, 
                                  ORMEnum.SQLALCHEMY,
                                  configuration)
        database.load_entity(*configuration['entities'])
        database.run_database()
        return database