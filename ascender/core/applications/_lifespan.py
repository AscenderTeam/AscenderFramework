from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

if TYPE_CHECKING:
    from ascender.core import Application


def create_lifespan(application: "Application"):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        for event in application.events["startup"]:
            await event()
        yield
        for event in application.events["shutdown"]:
            await event()

    return lifespan
