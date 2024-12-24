from abc import ABC, abstractmethod
from starlette.types import ASGIApp, Receive, Scope, Send


class AscenderMiddleware(ABC):
    app: ASGIApp
    
    @abstractmethod
    def __init__(self):
        ...
    
    def __post_init__(self):
        pass
    
    @abstractmethod
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> ASGIApp | None:
        pass