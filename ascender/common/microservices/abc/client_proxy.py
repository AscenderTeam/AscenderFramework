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
    """
    Represents a client proxy object for sending messages, emitting events to receivers on the other side.

    NOTE: Some transports may not support all features. For more information, refer to the documentation of each transport ([Kafka](#kafkatransporter), [Redis](#redistransporter) and [TCP](#tcptransporter)).
    """
    
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
        """
        Emit event to the broker without pairing and waiting for response.

        Args:
            pattern (str): Message pattern
            data (Any | BaseDTO | BaseResponse | None, optional): Data payload if there is. Defaults to None.
        """
        ...

    async def send(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 20.0,
        response_type: type[T] = Any,
    ) -> T:
        """
        Sends message pattern request and waits for result, then returns it.

        Args:
            pattern (str): A topic pattern which mostly used in message brokers.
            data (Any | BaseDTO | BaseResponse | None, optional): Data which contains requests payload, if provided. Defaults to None.
            timeout (float, optional): Response timeout in seconds. Defaults to 5.0.

        Returns:
            Any: Response data
        """
        raise NotImplementedError("Method is not implemented.")
    
    async def send_as_observable(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 20.0,
        response_type: type[T] = Any,
    ) -> Observable[T]:
        """
        Sends message pattern request and returns RxPY (Reactivex) observable object.

        Args:
            pattern (str): A topic pattern which mostly used in message brokers.
            data (Any | BaseDTO | BaseResponse | None, optional): Data which contains requests payload, if provided. Defaults to None.
            timeout (float, optional): Response timeout in seconds. Defaults to 5.0.
        """
        raise NotImplementedError("Method is not implemented.")
    
    def unwrap(self, rtype: type[T]) -> T:
        """
        Unwraps the transport instance to the requested type.

        Args:
            rtype (type[T]): The type to unwrap to.

        Raises:
            NotImplementedError: If the unwrapping is not implemented.

        Returns:
            T: The unwrapped transport instance.
        """
        raise NotImplementedError("Method is not implemented.")