from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, final

from fastapi.params import Depends

from ascender.core.applications.root_injector import RootInjector
from ascender.core.registries.service import ServiceRegistry
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.utils.module import load_module


class Guard(ABC):

    __di_module__: AscModuleRef | None = None
    __declaration_type__: str = "guard"

    def __init__(self):
        """
        For Guard configurations and parameters
        """
        ...
    
    def __post_init__(self):
        """
        For DI injections and dependency management
        """
        ...

    def can_activate(self):
        raise NotImplementedError("This method should be implemented in the subclass to determine if the guard can be activated.")
    
    @final
    def handle_di(self):
        if not self.__di_module__:
            return RootInjector().existing_injector.inject_factory_def(self.__post_init__)() # type: ignore
        
        di_module = self.__di_module__
        
        # Load module or if it's already loaded then just use it and ignore `RuntimeError: module is already loaded`
        try:
            di_module = load_module(di_module) # type: ignore
        except RuntimeError:
            pass
        
        # Execute `self.__post_init__` method
        self.__di_module__._injector.inject_factory_def(self.__post_init__)() # type: ignore
    
    def __call__(self, executable: Callable[..., None]) -> Any:
        if not getattr(executable, "__cmetadata__", None):
            executable.__cmetadata__ = {"dependencies": [Depends(self.handle_di), Depends(self.can_activate)]}
        
        else:
            if not executable.__cmetadata__.get("dependencies", None):
                executable.__cmetadata__["dependencies"] = [Depends(self.handle_di), Depends(self.can_activate)]
                return executable
            
            executable.__cmetadata__["dependencies"] = [*executable.__cmetadata__["dependencies"], Depends(self.handle_di), Depends(self.can_activate)]
        
        @wraps(executable)
        async def wrapper(*args, **kwargs):
            return await executable(*args, **kwargs) # type: ignore

        return wrapper