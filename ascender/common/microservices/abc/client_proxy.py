from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

from reactivex import Observable

from ascender.common.base.dto import BaseDTO
from ascender.common.base.response import BaseResponse
from ascender.common.microservices.instances.bus import SubscriptionEventBus

if TYPE_CHECKING:
    from ascender.common.microservices.instances.transport import TransportInstance


T = TypeVar("T")

class Undefined: ...


class ClientProxy(ABC):
    def __init__(
        self, 
        event_bus: SubscriptionEventBus,
        configs: dict[str, Any] = {},
        instance: "TransportInstance | None" = None,
    ):
        self.event_bus = event_bus
        self.configs = configs
        self.instance = instance
    
    @abstractmethod
    async def connect(self):
        ...
    
    @abstractmethod
    async def disconnect(self):
        ...
    
    @abstractmethod
    async def emit(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 20.0
    ) -> None:
        ...

    async def send(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 20.0,
        response_type: type[T] = Any,
    ) -> T:
        raise NotImplementedError("Method is not implemented.")
    
    async def send_as_observable(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 20.0,
        response_type: type[T] = Any,
    ) -> Observable[T]:
        raise NotImplementedError("Method is not implemented.")
    
    def unwrap(self, rtype: type[T]) -> T:
        raise NotImplementedError("Method is not implemented.")