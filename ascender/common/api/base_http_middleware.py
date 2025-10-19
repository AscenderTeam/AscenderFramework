from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint, Request, Response

from ascender.abc.middleware import AscenderMiddleware


class AscenderHTTPMiddleware(AscenderMiddleware):
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        return NotImplementedError() # pragma: no cover
    
    async def __call__(self, scope, receive, send):
        return await BaseHTTPMiddleware(self.app, self.dispatch)(scope, receive, send)