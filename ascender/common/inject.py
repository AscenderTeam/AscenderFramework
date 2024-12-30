from typing import Literal, TypeVar
from ascender.core.di.hierarchy_module import HierarchyModule
from ascender.core.registries.service import ServiceRegistry


T = TypeVar("T")
C = TypeVar("C")


class Inject:
    """
    Dependency Injector for seamless and lazy-loaded injections in non-injectable classes
    """
    def __init__(self, ignore_types: list[type[T]] = [], inject_type: Literal["lazy", "lazy-fn"] = "lazy"):
        self.ignore_types = ignore_types
        self.inject_type = inject_type
    
    def inject_from_di(self, di_module: HierarchyModule, cls: type[C]) -> C | type[C]:
        if self.inject_type == "lazy":
            di_module._lazy_loading_dependencies.append(cls)
            return cls
        
        if self.inject_type == "lazy-fn":
            di_module._lazy_loading_dependencies.append(cls.__post_init__)
            return cls
        
        return cls
    
    def inject_from_singletone(self, service_registry: ServiceRegistry, cls: type[C]) -> C | type[C]:
        if self.inject_type == "lazy":
            parameters = service_registry.get_parameters(cls)
            
            for name, obj in parameters.items():
                if type(obj) in self.ignore_types:
                    continue

                setattr(cls, name, obj)
            
            return cls
        
        if self.inject_type == "lazy-fn":
            parameters = service_registry.get_parameters(cls.__post_init__)
            
            cls.__post_init__(**parameters)
            return cls

    def inject_di(self, cls: C):
        di_module = getattr(cls, "__di_module__", None)

        if not di_module:
            return self.inject_from_singletone(ServiceRegistry())
        
        return self.inject_from_di(di_module, cls)

    def __call__(self, cls):
        cls = self.inject_di(cls)
        cls.__modular_injections__ = True
        return cls