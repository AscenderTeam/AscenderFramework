from starlette.middleware.cors import CORSMiddleware
from ascender.abc.middleware import AscenderMiddleware

import typing


class AscenderCORSMiddleware(AscenderMiddleware):
    def __init__(
        self,
        allow_origins: typing.Sequence[str] = (),
        allow_methods: typing.Sequence[str] = ("GET",),
        allow_headers: typing.Sequence[str] = (),
        allow_credentials: bool = False,
        allow_origin_regex: typing.Optional[str] = None,
        expose_headers: typing.Sequence[str] = (),
        max_age: int = 600,
    ):
        self.middleware_instance = CORSMiddleware
        self.middleware_params = {
            "allow_origins": allow_origins,
            "allow_methods": allow_methods,
            "allow_headers": allow_headers,
            "allow_credentials": allow_credentials,
            "allow_origin_regex": allow_origin_regex,
            "expose_headers": expose_headers,
            "max_age": max_age
        }
    
    async def __call__(self, scope, receive, send):
        return await self.middleware_instance(self.app, **self.middleware_params)(scope, receive, send)