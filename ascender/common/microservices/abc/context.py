from pydantic import BaseModel

from ascender.common.microservices.abc.event_transport import EventTransport
from ascender.common.microservices.abc.rpc_transport import RPCTransport


class BaseContext(BaseModel):
    """Just a stub object, all contexts should inherited of. Used for detecting contexts during `@MessagePattern`'s callback inspection to detect if it's context or not"""
    
    model_config = {"arbitrary_types_allowed": True}

    pattern: str
    correlation_id: str | None = None
    rpc_transport: RPCTransport
    event_transport: EventTransport
    is_event: bool