from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from reactivex import Observable

from ascender.common.base.dto import BaseDTO
from ascender.common.base.response import BaseResponse
from ascender.common.microservices.exceptions.rpc_exception import RPCException
from ascender.common.microservices.types.consumer_metadata import ConsumerMetadata

if TYPE_CHECKING:
    from ascender.common.microservices.abc.context import BaseContext
    from ascender.common.microservices.instances.bus import SubscriptionEventBus
    from ascender.common.microservices.abc.transporter import BaseTransporter
    from ascender.common.microservices.abc.client_proxy import ClientProxy


class RPCTransport(ABC):
    event_bus: "SubscriptionEventBus"

    def __init__(self, transport: "BaseTransporter | ClientProxy"):
        self.transport = transport
        self.event_bus = self.transport.event_bus
        self.event_bus.subscribe("_rpc:response", self.listen_for_requests)
    
    @abstractmethod
    async def send_request(
        self, 
        pattern: str, 
        data: dict | BaseResponse | BaseDTO,
        timeout: float = 4000
    ) -> dict | BaseResponse | BaseDTO:
        """Send an RPC request and return the response."""
        ...
    
    @abstractmethod
    async def send_nack_request(
        self, 
        pattern: str, 
        data: dict | BaseResponse | BaseDTO,
        timeout: float = 4000
    ) -> Observable[dict | BaseResponse | BaseDTO]:
        """Send an RPC request and return the response."""
        ...
    
    @abstractmethod
    async def listen_for_requests(self, context: "BaseContext", data: Any, metadata: ConsumerMetadata) -> None:
        """
        Listen on a topic for incoming requests.
        The `request_handler` is an async callback that process a request and return a response.
        """
        ...
    
    @abstractmethod
    async def send_response(self, pattern: str, correlation_id: str, response: bytes) -> None:
        """Send a response back to the caller, using the correlation id to route it."""
        ...

    @abstractmethod
    async def raise_exception(self, pattern: str, correlation_id: str, exception: RPCException):
        """
        Send an RPC error message back into RPC sender (producer) side, while also assigning metadata.
        NOTE: Only RPCException can be used and sent!
        """
    
    @abstractmethod
    async def process_response(self, correlation_id: str, response: Any, **kwargs):
        """Made for processing response"""
        ...