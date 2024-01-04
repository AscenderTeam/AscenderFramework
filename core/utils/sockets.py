from typing import Any, Awaitable, Callable, Optional, Text
from pydantic import BaseModel

from socketio import AsyncServer

Data = dict | str | list | int | float | bool | bytes

class Listen:
    def __init__(self, event: Text, *, use_namespace: bool = True, namespace: Optional[str] = None, all_namespaces: bool = False) -> None:
        self.event = event
        self.use_namespace = use_namespace
        self.namespace = namespace
        self.all_namespaces = all_namespaces
    
    def __call__(self, handler: Callable | Awaitable):
        handler.is_socketio = True
        handler._socketio_kwargs = {
            "event": self.event,
            "namespace": "[ALL]" if self.all_namespaces else self.namespace,
            "use_namespace": self.use_namespace
        }
        return handler

class ApplicationContext:
    def __init__(self, 
                 sid: str,
                 sio: AsyncServer,
                 event: str,
                 environ: dict | None,
                 namespace: str | None) -> None:
        self._sio = sio
        self._sid = sid
        self._environ = environ
        self._namespace = namespace
        self._event = event
    
    @property
    def namespace(self) -> str | None:
        return self._namespace

    @property
    def environ(self) -> dict | None:
        return self._environ
    
    @property
    def sid(self) -> str:
        return self._sid

    @property
    def event(self) -> str:
        return self._event
    
    async def emit(self, event: str, 
                   data: Optional[Data | BaseModel] = None,
                   to: Optional[str] = None, room: Optional[str] = None,
                   skip_sid: bool = False, namespace: Optional[str] = None, **kwargs):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        
        await self._sio.emit(event, data, to=to, room=room, skip_sid=skip_sid, namespace=namespace or self._namespace, **kwargs)
    
    async def call(self, event: str, data: Optional[Data | BaseModel] = None,
                   to: Optional[str] = None, sid: Optional[str] = None,
                   namespace: Optional[str] = None, timeout: int = 60):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        
        await self._sio.call(event, data, sid=sid, to=to, namespace=namespace or self._namespace, timeout=timeout)

    async def enter_room(self, room: str, sid: Optional[str] = None, namespace: Optional[str] = None):
        await self._sio.enter_room(sid=self._sid if not sid else sid, room=room, namespace=namespace or self._namespace)
    
    async def leave_room(self, room: str, sid: Optional[str] = None, namespace: Optional[str] = None):
        await self._sio.leave_room(sid=self._sid if not sid else sid, room=room, namespace=namespace or self._namespace)

    async def disconnect(self, sid: Optional[str] = None, namespace: Optional[str] = None):
        await self._sio.disconnect(sid=self._sid if not sid else sid, namespace=namespace or self._namespace)
    
    async def close_room(self, room: str, namespace: Optional[str] = None):
        await self._sio.close_room(room=room, namespace=namespace or self._namespace)

    async def rooms(self, sid: Optional[str] = None, namespace: Optional[str] = None):
        return await self._sio.rooms(sid=self._sid if not sid else sid, namespace=namespace or self._namespace)

    async def get_session(self, sid: Optional[str] = None, namespace: Optional[str] = None):
        return await self._sio.get_session(sid=self._sid if not sid else sid, namespace=namespace or self._namespace)

    async def save_session(self, session: Any, sid: Optional[str] = None, namespace: Optional[str] = None):
        await self._sio.save_session(session=session, sid=self._sid if not sid else sid, namespace=namespace or self._namespace)

    async def sleep(self, seconds: int = 0):
        await self._sio.sleep(seconds)
    
    async def session(self, sid: Optional[str] = None, namespace: Optional[str] = None):
        return await self._sio.session(sid=self._sid if not sid else sid, namespace=namespace or self._namespace)

    async def send(self, data: Data | BaseModel, room: Optional[str] = None, skip_sid: bool = False, namespace: Optional[str] = None, **kwargs):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        
        await self._sio.send(data, room=room, skip_sid=skip_sid, namespace=namespace or self._namespace, **kwargs)

    async def answer(self, event: str, 
                   data: Optional[Data | BaseModel] = None,
                   skip_sid: bool = False, namespace: Optional[str] = None, **kwargs):
        if isinstance(data, BaseModel):
            data = data.model_dump()
        
        await self._sio.emit(event, data, to=self.sid, skip_sid=skip_sid, namespace=namespace or self._namespace, **kwargs)
    