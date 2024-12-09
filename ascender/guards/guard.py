from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, final

from fastapi.params import Depends

from ascender.core.registries.service import ServiceRegistry
if TYPE_CHECKING:
    from ascender.core.di.hierarchy_module import HierarchyModule


class Guard(ABC):

    __di_module__: "HierarchyModule" = None
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
            params = ServiceRegistry().get_parameters(self.__post_init__)

            return self.__post_init__(**params)
        
        params = self.__di_module__.inject(self.__post_init__)

        self.__post_init__(**params)
    
    def __call__(self, executable: Callable[..., None]) -> Any:
        if not getattr(executable, "_dependencies", None):
            setattr(executable, "_dependencies", [Depends(self.handle_di), Depends(self.can_activate)])
            return executable
        setattr(executable, "_dependencies", [*getattr(executable, "_dependencies"), Depends(self.handle_di), Depends(self.can_activate)])
        
        @wraps(executable)
        async def wrapper(*args, **kwargs):
            return await executable(*args, **kwargs)

        return wrapper