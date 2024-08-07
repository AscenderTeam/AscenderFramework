from typing import Self, TypeVar
from core.application import Application
from core.extensions.repositories import IdentityRepository, Repository
from core.extensions.services import Service

I = TypeVar("I")


class PluginInjector:
    def __init__(self, application: Application) -> None:
        self.application = application
    
    def inject_mvc(self, interface: type[I], obj: I):
        self.application.service_registry.add_singletone(interface, obj)

    def unleash_update(self):
        for interface, service in self.application.service_registry.singletones.items():
            if isinstance(service, (Service, Repository, IdentityRepository)):
                # print(interface)
                parameters = self.application.service_registry.get_parameters(service)
                for key, value in parameters.items():
                    setattr(service, key, value)