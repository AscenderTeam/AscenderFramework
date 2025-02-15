from typing import Any, Callable, Literal, Sequence, TypeVar

from ascender.core.applications.root_injector import RootInjector
from ascender.core.di.interface.provider import Provider
from ascender.core.struct.module_ref import AscModuleRef


T = TypeVar("T")


class Injectable:
    def __init__(
        self, 
        provided_in: Literal["root", "any"] | type[AscModuleRef] | None = None,
        provided_as: Provider | None = None
    ):
        self.provided_in = provided_in
        self.provider_meta = provided_as

    def __call__(self, cls: type[T]) -> type[T]:
        if not self.provided_in:
            return cls
        
        if isinstance(self.provided_in, str):
            if self.provided_in == "root":
                self._register_in_root(cls)
        elif hasattr(self.provided_in, "__asc_module__"):
            self._register_in_module(cls)
        else:
            raise ValueError(f"Invalid `provided_in`: {self.provided_in}")
        return cls

    def _self_provider(self, cls):
        if self.provider_meta and self.provider_meta.get("provide"):
            if "@SELF" in self.provider_meta["provide"]:
                self.provider_meta["provide"] = cls

        return {"provide": cls, "use_class": cls} if not self.provider_meta else self.provider_meta

    def _register_in_root(self, cls: type[T]):
        root_injector = RootInjector()
        if cls not in root_injector.providers:
            root_injector.providers.append(self._self_provider(cls))

    def _register_in_module(self, cls: type[T]):
        if not hasattr(self.provided_in, "__asc_module__"):
            raise ValueError("The module must have `__asc_module__` defined.")
        asc_module = self.provided_in.__asc_module__
        if cls not in asc_module.providers:
            asc_module.providers.append(self._self_provider(cls))