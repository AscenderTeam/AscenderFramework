from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, final

from fastapi.params import Depends

from ascender.core.applications.root_injector import RootInjector
from ascender.core.registries.service import ServiceRegistry
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.utils.module import load_module


class Guard(ABC):

    __di_module__: AscModuleRef = None
    __declaration_type__: str = "guard"

    @abstractmethod
    def __init__(self):
        """
        For Guard configurations and parameters
        """
        ...
    
    @abstractmethod
    def __post_init__(self):
        """
        For DI injections and dependency management
        """
        ...

    @abstractmethod
    def can_activate(self):
        ...
    
    @final
    def handle_di(self):
        if not self.__di_module__:
            return RootInjector().existing_injector.inject_factory_def(self.__post_init__)
        
        di_module = self.__di_module__
        
        # Load module or if it's already loaded then just use it and ignore `RuntimeError: module is already loaded`
        try:
            di_module = load_module(di_module)
        except RuntimeError:
            pass
        
        # Execute `self.__post_init__` method
        self.__di_module__._injector.inject_factory_def(self.__post_init__)
    
    def __call__(self, executable: Callable[..., None]) -> Any:
        if not getattr(executable, "_dependencies", None):
            setattr(executable, "_dependencies", [Depends(self.handle_di), Depends(self.can_activate)])
            return executable
        setattr(executable, "_dependencies", [*getattr(executable, "_dependencies"), Depends(self.handle_di), Depends(self.can_activate)])
        
        @wraps(executable)
        async def wrapper(*args, **kwargs):
            return await executable(*args, **kwargs)

        return wrapper