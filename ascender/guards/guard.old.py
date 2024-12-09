from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Self

from fastapi import Depends

from ascender.core.registries.service import ServiceRegistry


class Guard(ABC):
    service_registry: ServiceRegistry

    @abstractmethod
    async def handle_access(self):
        ...
    
    def __call__(self, executable: Callable[..., None]) -> Any:
        self.service_registry = ServiceRegistry()
        if not getattr(executable, "_dependencies", None):
            setattr(executable, "_dependencies", [Depends(self.handle_access)])
            return executable
        setattr(executable, "_dependencies", [*getattr(executable, "_dependencies"), Depends(self.handle_access)])
        
        @wraps(executable)
        async def wrapper(*args, **kwargs):
            return await executable(*args, **kwargs)

        return wrapper