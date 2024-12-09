from typing import TYPE_CHECKING
from ascender.abstracts.factory import AbstractFactory
from ascender.abstracts.module import AbstractModule
from ascender.contrib.repositories import Repository
from ascender.core.database.engine import DatabaseEngine
from ascender.core.database.types.orm_enum import ORMEnum

if TYPE_CHECKING:
    from ascender.core.application import Application

class ProvideRepository(AbstractModule, AbstractFactory):

    database_engine: DatabaseEngine

    def __init__(self, repository: type[Repository]):
        self.repository = repository
    
    def on_application_bootstrap(self, application: "Application"):
        if self.database_engine.orm == ORMEnum.SQLALCHEMY:
            context = self.database_engine.generate_context()
            repository = self.repository(context)
            self.factory_add(self.repository, repository)
            return
        
        repository = self.repository(None)
        self.factory_add(self.repository, repository)
    
    def on_module_init(self):
        return super().on_module_init()
    
    def on_application_shutdown(self, application):
        return super().on_application_shutdown(application)