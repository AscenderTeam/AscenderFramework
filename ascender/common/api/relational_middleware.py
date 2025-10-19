from typing import Any
from ascender.abc.middleware import AscenderMiddleware


class FromFastAPIMiddleware(AscenderMiddleware):
    def __init__(self, middleware: type[Any], **middleware_arguments):
        self.middleware_instance = middleware
        self.middleware_arguments = middleware_arguments
    
    async def __call__(self, scope, receive, send):
        return await self.middleware_instance(self.app, **self.middleware_arguments)(scope, receive, send)