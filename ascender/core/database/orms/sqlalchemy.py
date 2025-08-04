import importlib
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker

from ascender.core.database.entity import DBEntity


class SQLAlchemyORM:
    engine: AsyncEngine | None
    models: list[DBEntity]

    def __init__(self, configuration: dict) -> None:
        self.configuration = configuration
        if configuration["type"] == "dbstring":
            self.engine = create_async_engine(configuration["content"], **configuration.get("pool_options", {}))
        # else:
        # TODO: Add manual type support
        self.SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=self.engine, class_=AsyncSession)
        self.metadata = DBEntity.metadata
        self.models = []
    
    def load_entities(self, *entity_modules):
        for module_name in entity_modules:
            module = importlib.import_module(module_name)
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isinstance(attribute, type(DBEntity)) and issubclass(attribute, DBEntity):
                    self.models.append(attribute)
    
    async def run_database(self):
        async with self.engine.begin() as conn:
            for model in self.models:
                await conn.run_sync(model.metadata.create_all)
    
    async def shutdown_database(self):
        await self.engine.dispose()
    
    def get_session(self):
        return self.SessionLocal()