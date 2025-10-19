from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from ascender.common.microservices.abc.context import BaseContext
from ascender.common.microservices.types.consumer_metadata import ConsumerMetadata

if TYPE_CHECKING:
    from ascender.common.microservices.instances.transport import TransportInstance


class TransportEventBus(ABC):

    @abstractmethod
    async def emit(self, context: BaseContext, topic: str, data: Any, metadata: ConsumerMetadata) -> None:
        """Emit (publish) an event on a given topic."""
        pass

    @abstractmethod
    def subscribe(self, topic: str, callback: Callable[["TransportInstance", dict, Any], Awaitable[None]]) -> str:
        """Subscribe to a topic. When a message arrives, invoke the callback."""
        pass

    @abstractmethod
    def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from a given topic."""
        pass