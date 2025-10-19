from typing import Sequence
from ascender.abc.middleware import AscenderMiddleware
from starlette.types import ASGIApp

from ascender.core.di.interface.provider import Provider


def useMiddlewares(*middlewares: AscenderMiddleware) -> Sequence[Provider]:
    def middleware_factory(middleware: AscenderMiddleware):
        def middleware_wrapper(app: ASGIApp):
            middleware.app = app
            return middleware
        
        return middleware_wrapper
    
    return [
        {
            "provide": "ASC_MIDDLEWARE",
            "value": middleware_factory(middleware),
            "multi": True
        } for middleware in middlewares
    ]