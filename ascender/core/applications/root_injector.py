from typing import Any, MutableSequence, Self, TypeVar
from ascender.core.di.abc.base_injector import Injector
from ascender.core.di.create import create_injector
from ascender.core.di.injector import AscenderInjector
from ascender.core.di.interface.consts import RAISE_NOT_FOUND
from ascender.core.di.interface.injector import InjectorOptions
from ascender.core.di.interface.provider import Provider


T = TypeVar("T")


class RootInjector:
    _instance: Self | None = None
    _injector: AscenderInjector | None = None
    providers: MutableSequence[Provider] = []
    
    def __init__(self) -> None:
        self.scope = "root"

    def __new__(cls) -> Self:
        if not cls._instance:
            cls._instance = super(RootInjector, cls).__new__(cls)
        
        return cls._instance
    
    def create(self, providers: list[Provider]):
        self._injector = create_injector(
            (*(provider for provider in providers if provider is not None), *self.providers)
        )
        
        return self

    def get(
        self,
        token: type[T] | str | Any,
        not_found_value: Any | None = RAISE_NOT_FOUND,
        options: InjectorOptions = {
            "optional": False
        }
    ) -> T | Any | None:
        assert self._injector
        return self._injector.get(token, not_found_value, options)
    
    @property
    def injector(self):
        return self._injector
    
    @property
    def existing_injector(self):
        assert self._injector
        return self._injector