from abc import ABC, abstractmethod
from starlette.types import ASGIApp, Receive, Scope, Send


class AscenderMiddleware(ABC):
    app: ASGIApp
    
    def __init__(self):
        ...
    
    @abstractmethod
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> ASGIApp | None:
        pass