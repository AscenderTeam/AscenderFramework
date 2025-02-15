from typing import Sequence
from collections.abc import Sequence as _Sequence
from ascender.common.microservices.transport_manager import TransportManager
from ascender.common.microservices.types.transport import Transports
from ascender.core.di.injectfn import inject
from ascender.core.di.none_injector import NoneInjectorException
from ascender.core.struct.controller_hook import ControllerDecoratorHook


class EventPattern(ControllerDecoratorHook):
    def __init__(
        self, 
        pattern: str | int
    ):
        self.pattern = pattern
    
    def on_load(self, callable):
        try:
            transport_manager: TransportManager = inject("TRANSPORT_MANAGER")
        except NoneInjectorException:
            raise RuntimeError("Cannot use `MessagePattern` without defining microservices in application root bootstrap! Please make sure Ascender Framework's microservice module loaded correctly")
        
        transport_manager.add_event_pattern(self.pattern, callable)