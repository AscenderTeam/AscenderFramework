
from typing import List, TypeVar, TypedDict
from fastapi import APIRouter
from tortoise.models import Model as Entity

from core.extensions.repositories import Repository
from core.extensions.services import Service

class Controller(TypedDict):
    name: str
    base_path: str
    initialize_all_controllers: bool
    exclude_controllers: List[str]


class ControllerModule(TypedDict):
    name: str | None
    controller: object
    services: dict[str, type[Service]]
    repository: type[Repository] | None
    repository_entities: dict[str, Entity]