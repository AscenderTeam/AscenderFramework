from __future__ import annotations
from typing import TYPE_CHECKING, Coroutine, Optional

from fastapi_socketio import SocketManager
from ascender.core.utils.sockets import ApplicationContext

from settings import ORIGINS

if TYPE_CHECKING:
    from ascender.core.application import Application

class LoadedEndpoints:
    endpoints: list[dict] = []
    
    @staticmethod
    def add_event(namespace: Optional[str], event: str, handler: Coroutine) -> None:
        LoadedEndpoints.endpoints.append({
            "namespace": namespace,
            "event": event,
            "handler": handler
        })


class SocketIOApp:
    def __init__(self, app: Application, **options):
        self.app = app
        self.server = SocketManager(self.app.app, **options)
    
    def add_event(self, namespace: Optional[str], event: str, handler: Coroutine) -> None:
        self.app.app.sio.on(event, self.cb_handler(event, handler, namespace), namespace=namespace)
    
    def cb_handler(self, event: str, handler: Coroutine, namespace: str | None) -> Coroutine:

        async def wrapper(*args):
            ctx = ApplicationContext(args[0], self.app.app.sio, event, args[1] if event == "connect" else None, namespace)
            
            # Check if handler has 2 arguments (ctx, data)
            try:
                if event == "connect":
                    await handler(ctx, *args[2:])
                else:
                    await handler(ctx, *args[1:])
            
            except TypeError:
                await handler(ctx)

        return wrapper