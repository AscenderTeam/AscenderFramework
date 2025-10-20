from typing import Any

from fastapi import FastAPI
from ascender.core.database.dbcontext import AppDBContext
from ascender.core.database.errors.wrong_orm import WrongORMException
from ascender.core.database.orms.sqlalchemy import SQLAlchemyORM
from ascender.core.database.orms.tortoise import TortoiseORM
from ascender.core.database.types.orm_enum import ORMEnum


class DatabaseEngine:
    engine: TortoiseORM | SQLAlchemyORM

    def __init__(self, orm: ORMEnum, configuration: Any) -> None:
        """
        Initialize the DatabaseEngine.

        Args:
            orm (ORMEnum): The ORM to use (Tortoise or SQLAlchemy).
            configuration (Any): The configuration for the ORM.
        """
        self.orm = orm
        self.configuration = configuration
        self.engine = TortoiseORM(configuration) if orm == ORMEnum.TORTOISE else SQLAlchemyORM(configuration)
    
    def load_entity(self, *entity_modules):
        if not isinstance(self.engine, SQLAlchemyORM):
            raise WrongORMException("DatabaseEngine.load_entity(...)")
        
        self.engine.load_entities(*entity_modules)

    def run_database(self, app: FastAPI):
        if isinstance(self.engine, SQLAlchemyORM):
            app.add_event_handler("startup", self.engine.run_database)
            app.add_event_handler("shutdown", self.engine.shutdown_database)
        else:
            self.engine.run_database(app)
            
    async def run_database_manual(self):
        if isinstance(self.engine, SQLAlchemyORM):
            await self.engine.run_database()
        else:
            await self.engine.run_database_cli()
    
    def generate_context(self):
        """
        Generate a database context for SQLAlchemy ORM.

        Raises:
            WrongORMException: If the ORM is not SQLAlchemy.

        Returns:
            AppDBContext: The database context that carries database session for SQLAlchemy.
        """
        if not isinstance(self.engine, SQLAlchemyORM):
            raise WrongORMException("DatabaseEngine.generate_context()")
        _context = AppDBContext(self.engine)

        return _context