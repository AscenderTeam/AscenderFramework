from abc import ABC, abstractmethod
from typing import Callable, final
from ascender.core.router.interface.route import RouterRoute
from ascender.core.struct.controller_ref import ControllerRef


class ControllerDecoratorHook(ABC):
    controller: ControllerRef
    route_configuration: RouterRoute

    @abstractmethod
    def on_load(self, callable: Callable):
        raise NotImplementedError("Hook `on_load` was not implemented yet. Please define it!")

    @final
    def set_configurations(self, controller: ControllerRef, route_configuration: RouterRoute):
        self.controller = controller
        self.route_configuration = route_configuration

    def __call__(self, executable):
        executable.__hook_metadata__ = {
            "name": self.__class__.__name__,
            "callback": self.on_load,
            "setter": self.set_configurations
        }
        return executable