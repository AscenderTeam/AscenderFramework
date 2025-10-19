from sqlalchemy import Select
from ascender.core.database.orms.sqlalchemy import SQLAlchemyORM


class Constructor(Select):
    def __init__(self, engine: SQLAlchemyORM, *entities):
        self.engine = engine
        super().__init__(*entities)
    
    def __await__(self):
        async def execute_self():
            async with self.engine.get_session() as session:
                return await session.execute(self)
        return execute_self().__await__()