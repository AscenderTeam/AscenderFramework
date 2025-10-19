from typing import Self, TypeVar
import inspect

_Interface = TypeVar("_Interface")
_Class = TypeVar("_Class")


class ServiceRegistry:
    singletones: dict[_Interface, _Class] = {}
    scopes: None

    _instance: Self | None = None
    
    def __init__(self) -> None:
        self.scopes = None

    def __new__(cls) -> Self:
        if not cls._instance:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
        
        return cls._instance
    
    def add_singletone(self, interface: type[_Interface], obj: _Class):
        self.singletones[interface] = obj
    
    def resolve(self, interface: type[_Interface], 
                default: _Class | None = None) -> _Interface | _Class | None:
        singletone = self.get_singletone(interface)

        if not singletone:
            return default
        
        return singletone

    def get_singletone(self, interface: type[_Interface]) -> _Interface:
        if interface not in self.singletones:
            return None
        
        return self.singletones[interface]

    def get_parameters(self, obj: object) -> dict[str, _Interface]:
        obj_args = {}

        if inspect.isfunction(obj) or callable(obj):
            obj_args = inspect.signature(obj).parameters
        
        else:
            obj_args = obj.__class__.__annotations__
        
        args = {}
        for name, abstract in obj_args.items():
            # abstract: inspect.Parameter = abstract
            if isinstance(abstract, inspect.Parameter):
                abstract = abstract.annotation
            if abstract in self.singletones:
                args[name] = self.resolve(abstract)
        
        return args