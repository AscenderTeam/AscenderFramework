from typing import TypeVar

from ascender.core.registries.service import ServiceRegistry


T = TypeVar("T")


class Injectable:
    def __init__(self, forRoot: bool = True):
        self.for_root = forRoot
    
    def __call__(self, cls: type[T]):
        if self.for_root:
            # NOTE: This will add the class into global singleton
            cls._for_root = True

        cls._injectable = True
        cls.__modular_injections__ = True
        return cls