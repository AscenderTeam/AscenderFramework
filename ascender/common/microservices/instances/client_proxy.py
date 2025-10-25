from typing import Any

from reactivex import Observable

from ascender.common.base.dto import BaseDTO
from ascender.common.base.response import BaseResponse
from ascender.common.microservices.instances.transport import TransportInstance
from ascender.common.microservices.types.transport import Transports


class ClientProxy:
    """
    Represents a client proxy object for sending messages, emitting events to receivers on the other side.

    NOTE: Some transports may not support all features. For more information, refer to the documentation of each transport ([Kafka](#kafkatransporter), [Redis](#redistransporter) and [TCP](#tcptransporter)).
    """
    def __init__(self, transport: TransportInstance):
        self.transport = transport
        self.rpc_transport = None
        self.event_transport = None

        # Define all transports
        self.__define_transports()
    
    def __define_transports(self):
        match self.transport.transport["transport"]:
            case Transports.KAFKA:
                from .kafka.rpc import KafkaRPCTransport
                from .kafka.event import KafkaEventTransport
                self.rpc_transport = KafkaRPCTransport(self.transport)
                self.event_transport = KafkaEventTransport(self.transport)
            
            case Transports.REDIS:
                from .redis.rpc import RedisRPCTransport
                from .redis.event import RedisEventTransport
                self.rpc_transport = RedisRPCTransport(self.transport)
                self.event_transport = RedisEventTransport(self.transport)
            
    async def send(
        self, 
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 20.0
    ) -> Any | None:
        """
        Sends message pattern request and waits for result, then returns it.

        Args:
            pattern (str): A topic pattern which mostly used in message brokers.
            data (Any | BaseDTO | BaseResponse | None, optional): Data which contains requests payload, if provided. Defaults to None.
            timeout (float, optional): Response timeout in seconds. Defaults to 5.0.

        Returns:
            Any: Response data
        """
        return await self.rpc_transport.send_request(pattern, data, timeout)
    
    async def send_as_observable(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 5.0
    ) -> Observable[Any]:
        """
        Sends message pattern request and returns RxPY (Reactivex) observable object.

        Args:
            pattern (str): A topic pattern which mostly used in message brokers.
            data (Any | BaseDTO | BaseResponse | None, optional): Data which contains requests payload, if provided. Defaults to None.
            timeout (float, optional): Response timeout in seconds. Defaults to 5.0.
        """
        return await self.rpc_transport.send_nack_request(pattern, data, timeout)
    
    async def emit(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        **kwargs
    ):
        """
        Emit event to the broker without pairing and waiting for response.

        Args:
            pattern (str): Message pattern
            data (Any | BaseDTO | BaseResponse | None, optional): Data payload if there is. Defaults to None.
        """
        return await self.event_transport.send_event(pattern, data, **kwargs)
    
    async def emit_wait(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        **kwargs
    ):
        """
        Emits event to the broker while waiting for result of broker.
        """
        return await self.event_transport.send_event_with_defer(pattern, data, **kwargs)