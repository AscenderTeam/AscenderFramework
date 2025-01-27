from abc import ABC, abstractmethod
from typing import Awaitable, Callable
from httpx import Request, Response

InterceptorIn = Request
InterceptorFn = Awaitable[Callable[[Request], Request]]


class Interceptor(ABC):
    
    @abstractmethod
    async def handle_request(self, request: InterceptorIn) -> Request:
        raise NotImplementedError("Handle request is not implemented")
    
    async def handle_response(self, response: Response):
        return response