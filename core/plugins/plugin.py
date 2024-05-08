from __future__ import annotations
from logging import Logger, getLogger
from typing import TYPE_CHECKING, final

from core.extensions.repositories import Repository
from core.extensions.services import Service
from core.store.distributor import Distributor
from core.types import ControllerModule

if TYPE_CHECKING:
    from core.application import Application


class Plugin:
    # Overridable
    name: str
    description: str

    # Shouldn't be overrided
    logger: Logger
    
    # Overridable
    def install(self, application: Application, *args, **kwargs):
        raise NotImplementedError()
    
    def before_controller_load(self, name: str, instance: object, configuration: ControllerModule):
        pass

    def after_controller_load(self, name: str, instance: object, configuration: ControllerModule):
        pass

    def on_dependency_intialization(self, active_controllers: list[object]):
        pass