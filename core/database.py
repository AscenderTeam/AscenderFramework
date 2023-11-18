from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from settings import TORTOISE_ORM

def run_database(app: FastAPI):
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True
    )

async def run_database_cli():
    await Tortoise.init(config=TORTOISE_ORM)