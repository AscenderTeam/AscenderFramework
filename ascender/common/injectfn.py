from typing import TypeVar
from ascender.core.registries.service import ServiceRegistry


T = TypeVar("T")


def inject(__injectable: type[T]) -> T:
    service_registry = ServiceRegistry()
    return service_registry.resolve(__injectable, None)
