from typing import Any, AsyncGenerator, Awaitable, Generator, Generic
from typing_extensions import TypeVar
from sqlalchemy import Result, Select
from ascender.core.database.orms.sqlalchemy import SQLAlchemyORM


T = TypeVar("T")


class Constructor(Select, Generic[T]):
    """
    Constructor for the database query builder.
    """
    def __init__(self, engine: SQLAlchemyORM, *entities: type[T]) -> None:
        self.engine = engine
        super().__init__(*entities)

    def __await__(self):
        async def execute_self() -> Result[tuple[T]]:
            async with self.engine.get_session() as session:
                return await session.execute(self)
        return execute_self().__await__()