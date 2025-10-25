from typing import Sequence, TypeVar
from ascender.core.database.constructor import Constructor
from ascender.core.database.orms.sqlalchemy import SQLAlchemyORM

from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")

class AppDBContext:
    """
    Application Database Context for SQLAlchemy.
    
    Usage example:
    ```python
    from ascender.core.database import DatabaseEngine
    from .entities.users import UserEntity
    
    
    @Injectable(provided_in="root")
    class MyService:
        def __init__(self, engine: DatabaseEngine):
            self.context = engine.generate_context() # It's AppDBContext
            
        async def create_user(self, name: str):
            # creates user
            async with self.context() as db:
                entity = UserEntity(name)
                db.add(entity) # sqlalchemy session calls
                await db.commit() # sqlalchemy session calls
            
        async def fetch_user(self, id: int):
            query = self.context.construct(UserEntity) # After you call construct, it returns `Construction[UserEntity]` where you can apply query constrains (e.g. filter, where, limits and etc).
            
            query = await query.filter(UserEntity.id == id) # as soon as we `await` the `Construction[UserEntity]` it's no longer `Construction[UserEntity]` anymore, it's SQLAlchemy's `Result` object.
            
            return query.scalar() # Returns UserEntity or None, refer to SQLAlchemy's official documentation for more information about `Result` object.
    ```
    """
    def __init__(self, engine: SQLAlchemyORM) -> None:
        self.engine = engine

    def construct(self, *entities: type[T]) -> Constructor[T]:
        """
        Creates a Constructor for the given entities.
        
        As in given example above, after you call `construct` method, it returns `Constructor[T]` where you can apply query constrains (e.g. filter, where, limits and etc).
        As soon as you `await` the `Constructor[T]` it's no longer `Constructor[T]` anymore, it's SQLAlchemy's [Result](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Result) object, calling await is similar to doing `await session.execute(...)`.

        Returns:
            Constructor[T]: The constructed query builder.
        """
        return Constructor[T](self.engine, *entities)

    def __call__(self) -> AsyncSession:
        """
        Provides a new database session.

        Returns:
            AsyncSession: The new database [session](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session).
        """
        return self.engine.get_session()