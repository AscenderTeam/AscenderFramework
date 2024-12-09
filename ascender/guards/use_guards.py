from functools import wraps
from typing import Any, Callable
from ascender.guards.guard import Guard


class UseGuards:
    def __init__(self, *guards: Guard):
        self.guards = guards
    
    def __call__(self, executable: Callable[..., None]) -> Any:
        
        wrapped_executable = executable

        for guard in self.guards:
            wrapped_executable = guard(wrapped_executable)

        return wrapped_executable