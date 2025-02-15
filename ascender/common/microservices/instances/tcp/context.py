import asyncio
from pydantic import BaseModel
from ascender.common.microservices.abc.context import BaseContext
from ascender.common.microservices.instances.tcp.event import TCPEventTransport
from ascender.common.microservices.instances.tcp.rpc import TCPRPCTransport

class TCPContext(BaseContext):
    # TCP-specific fields.
    remote_addr: str = ""

    async def send(self, pattern: str, data=None, timeout: float = 4000):
        """
        Sends a response back to the caller using the underlying writer.
        """
        return await self.rpc_transport.send_request(pattern, data, timeout)

    async def send_as_observable(self, pattern: str, data=None, timeout: float = 4.0):
        # For TCP, simply send the response.
        return await self.rpc_transport.send_nack_request(pattern, data, timeout)

    async def defer_response(self):
        raise NotImplementedError("TCP transporter does not support deferring responses.")

    async def emit(self, pattern: str, data=None, **kwargs):
        """
        Emits an event back to the client.
        """
        return await self.event_transport.send_event(pattern, data, **kwargs)

    async def emit_wait(self, pattern: str, data=None, **kwargs):
        return await self.emit(pattern, data, **kwargs)