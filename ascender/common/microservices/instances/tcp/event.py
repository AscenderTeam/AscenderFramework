import json
import asyncio
from ascender.common.microservices.abc.event_transport import EventTransport
from ascender.common.microservices.utils.data_parser import parse_data
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ascender.common.microservices.instances.tcp.transporter import TCPTransporter
    from ascender.common.microservices.instances.tcp.client import TCPClient

class TCPEventTransport(EventTransport):
    def __init__(self, transport: "TCPClient | TCPTransporter",
            writer: asyncio.StreamWriter | None = None):
        super().__init__(transport)
        self.writer = writer if transport.__class__.__name__ == "TCPTransporter" else transport.writer

    async def send_event(self, pattern, data=None, **kwargs):
        envelope = {
            "pattern": pattern,
            "payload": parse_data(data),
        }
        message = json.dumps(envelope) + "\n"
        self.writer.write(message.encode())
        await self.writer.drain()

    async def send_event_with_defer(self, pattern, data=None, **kwargs):
        return await self.send_event(pattern, data, **kwargs)