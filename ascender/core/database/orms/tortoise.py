from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise


class TortoiseORM:
    def __init__(self, configuration: dict) -> None:
        self.configuration = configuration

    def run_database(self, app: FastAPI):
        register_tortoise(
            app,
            config=self.configuration,
            generate_schemas=True,
            add_exception_handlers=True
        )

    async def run_database_cli(self):
        await Tortoise.init(config=self.configuration)