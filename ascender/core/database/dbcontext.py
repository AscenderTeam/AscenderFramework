from ascender.core.database.constructor import Constructor
from ascender.core.database.orms.sqlalchemy import SQLAlchemyORM


class AppDBContext:
    def __init__(self, engine: SQLAlchemyORM) -> None:
        self.engine = engine
    
    def construct(self, *entities):
        return Constructor(self.engine, *entities)
    
    def __call__(self):
        return self.engine.get_session()