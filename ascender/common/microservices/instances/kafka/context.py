from typing import Any

from ascender.common.base.dto import BaseDTO
from ascender.common.base.response import BaseResponse
from ascender.common.microservices.abc.context import BaseContext
from ascender.common.microservices.instances.kafka.event import KafkaEventTransport
from ascender.common.microservices.instances.kafka.rpc import KafkaRPCTransport


class KafkaContext(BaseContext):

    pattern: str
    partition: int
    offset: int
    key: Any | None = None
    timestamp: int = 0
    timestamp_type: int = 0
    headers: list[tuple[str, bytes]] = []

    correlation_id: str | None = None
    rpc_transport: KafkaRPCTransport
    event_transport: KafkaEventTransport
    is_event: bool = False

    async def send(
        self, 
        pattern: str, 
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 10
    ):
        """
        Sends message pattern request and waits for result, then returns it.

        Args:
            pattern (str): _description_
            data (Any | BaseDTO | BaseResponse | None, optional): _description_. Defaults to None.
            timeout (float, optional): _description_. Defaults to 4000.

        Returns:
            Any: Response data
        """
        return await self.rpc_transport.send_request(pattern, data, timeout)
    
    async def send_as_observable(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        timeout: float = 10
    ):
        """
        Sends request and returns observable to handle response

        Args:
            pattern (str): Topic pattern where to send
            data (Any | BaseDTO | BaseResponse | None, optional): Data payload if there is. Defaults to None.
            timeout (float, optional): Timeout in seconds. Defaults to 4.0.

        Returns:
            Observable: Reactivex (RxPY) observable object
        """
        return await self.rpc_transport.send_nack_request(pattern, data, timeout)
    
    async def defer_response(self):
        """
        Defers response if there's intense task which requires more time to process.
        In order to avoid timeout error in producer side.
        """
        if self.is_event:
            raise ValueError("Failed to defer response. Make sure you're trying to defer response from message handler!")
        
        return await self.rpc_transport.defer(self.pattern, self.correlation_id)

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