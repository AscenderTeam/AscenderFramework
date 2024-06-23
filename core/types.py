from typing import Any, List, NotRequired, TypedDict
from tortoise.models import Model as Entity

from core.extensions.repositories import Repository
from core.extensions.services import Service

class Controller(TypedDict):
    name: str
    base_path: str
    initialize_all_controllers: bool
    exclude_controllers: List[str]


class ControllerModule(TypedDict):
    controller: object
    services: dict[str, type[Service]]
    repository: type[Repository] | None
    repository_entities: dict[str, type[Entity]]
    plugin_configs: NotRequired[dict[str, Any]]