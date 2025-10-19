from abc import ABC
from typing import TYPE_CHECKING, Any

from ascender.common.base.dto import BaseDTO
from ascender.common.base.response import BaseResponse
if TYPE_CHECKING:
    from ascender.common.microservices.instances.bus import SubscriptionEventBus
    from ascender.common.microservices.abc.client_proxy import ClientProxy
    from ascender.common.microservices.abc.transporter import BaseTransporter


class EventTransport(ABC):
    event_bus: "SubscriptionEventBus"

    def __init__(self, transport: "BaseTransporter | ClientProxy"):
        self.transport = transport
        self.event_bus = self.transport.event_bus
    
    async def send_event(
        self, 
        pattern: str, 
        data: Any | BaseDTO | BaseResponse | None = None,
        **kwargs
    ):
        raise NotImplementedError("Method is not implemented")
    
    async def send_event_with_defer(
        self,
        pattern: str,
        data: Any | BaseDTO | BaseResponse | None = None,
        **kwargs
    ):
        raise NotImplementedError("Method is not implemented")