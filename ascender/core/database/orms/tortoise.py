from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise


class TortoiseORM:
    def __init__(self, app: FastAPI, configuration: dict) -> None:
        self.app = app
        self.configuration = configuration

    def run_database(self):
        register_tortoise(
            self.app,
            config=self.configuration,
            generate_schemas=True,
            add_exception_handlers=True
        )

    async def run_database_cli(self):
        await Tortoise.init(config=self.configuration)