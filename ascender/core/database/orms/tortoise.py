from typing import TYPE_CHECKING

from tortoise import Tortoise
from tortoise.contrib.fastapi import RegisterTortoise

if TYPE_CHECKING:
    from ascender.core.applications.application import Application


class TortoiseORM:
    def __init__(self, configuration: dict) -> None:
        self.configuration = configuration

    def run_database(self, app: "Application"):
        orm = RegisterTortoise(
            app=app.app,
            config=self.configuration,
            generate_schemas=True,
            add_exception_handlers=True,
        )

        app.add_event_handler("startup", orm.init_orm)
        app.add_event_handler("shutdown", orm.close_orm)

    async def run_database_cli(self):
        await Tortoise.init(config=self.configuration)
