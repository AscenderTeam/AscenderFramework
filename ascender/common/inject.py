from typing import TypeVar
from ascender.core.registries.service import ServiceRegistry


T = TypeVar("T")
C = TypeVar("C")


class Inject:
    def __init__(self, ignore_types: list[type[T]] = []):
        self.ignore_types = ignore_types
    
    def __call__(self, cls: C):
        service_registry = ServiceRegistry()
        parameters = service_registry.get_parameters(cls)
        
        for name, obj in parameters.items():
            if type(obj) in self.ignore_types:
                continue
            
            setattr(cls, name, obj)
        
        cls.__modular_injections__ = True
        return cls