from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

from ascender.common.microservices.instances.bus import SubscriptionEventBus

if TYPE_CHECKING:
    from ascender.common.microservices.instances.transport import TransportInstance


T = TypeVar("T")

class BaseTransporter(ABC):
    def __init__(
        self, 
        instance: "TransportInstance",
        event_bus: SubscriptionEventBus,
        configs: dict[str, Any] = {}, 
    ):
        self.instance = instance
        self.event_bus = event_bus
        self.configs = configs
    
    @abstractmethod
    async def listen(self):
        ...
    
    @abstractmethod
    async def close(self):
        ...
    
    async def on(self, event: str, callback: Callable[..., Awaitable[Any | None]]):
        raise NotImplementedError("Method is not implemented.")

    def unwrap(self, rtype: T) -> T:
        raise NotImplementedError("Method is not implemented.")