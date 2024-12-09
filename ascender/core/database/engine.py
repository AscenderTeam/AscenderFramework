from typing import Any

from fastapi import FastAPI
from ascender.core.database.dbcontext import AppDBContext
from ascender.core.database.errors.wrong_orm import WrongORMException
from ascender.core.database.orms.sqlalchemy import SQLAlchemyORM
from ascender.core.database.orms.tortoise import TortoiseORM
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.contrib.repositories import IdentityRepository


class DatabaseEngine:
    engine: TortoiseORM | SQLAlchemyORM

    def __init__(self, app: FastAPI, orm: ORMEnum, configuration: dict[str, Any]) -> None:
        self.app = app
        self.orm = orm
        self.configuration = configuration
        self.engine = TortoiseORM(self.app, configuration) if orm == ORMEnum.TORTOISE else SQLAlchemyORM(configuration)
    
    def load_entity(self, *entity_modules):
        if not isinstance(self.engine, SQLAlchemyORM):
            raise WrongORMException("DatabaseEngine.load_entity(...)")
        
        self.engine.load_entities(*entity_modules)

    def run_database(self):
        if isinstance(self.engine, SQLAlchemyORM):
            self.app.add_event_handler("startup", self.engine.run_database)
            self.app.add_event_handler("shutdown", self.engine.shutdown_database)
        else:
            self.engine.run_database()
    
    def generate_context(self):
        if not isinstance(self.engine, SQLAlchemyORM):
            raise WrongORMException("DatabaseEngine.generate_context()")
        _context = AppDBContext(self.engine)

        return _context
    
    def identity_repo(self, _repo: type[IdentityRepository]):
        if isinstance(self.engine, SQLAlchemyORM):
            return _repo(self.generate_context())
        
        return _repo()