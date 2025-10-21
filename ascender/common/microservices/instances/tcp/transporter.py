import asyncio
import json
import traceback
from inspect import isclass
from typing import TypeVar

from ascender.common.microservices.abc.transporter import BaseTransporter
from ascender.common.microservices.instances.tcp.context import TCPContext
from ascender.common.microservices.instances.tcp.event import TCPEventTransport
from ascender.common.microservices.instances.tcp.rpc import TCPRPCTransport


T = TypeVar("T")


class TCPTransporter(BaseTransporter):
    """
    Basic TCP Transporter implementation working on ascender framework's request correlation model.
    
    Supports both RPC and Event message patterns.

    Raises:
        TypeError: If the requested underlying transporter instance type is unknown.
    
    NOTE: 
        Current type of transporter and implementation is on beta stage and may change in future releases. Use it with caution.
    """
    is_stopped: bool = True

    def __init__(self, instance, event_bus, configs: dict = {}):
        super().__init__(instance, event_bus, configs)
        self.host = self.configs.get("host", "0.0.0.0")
        self.port = self.configs.get("port", 8888)
        self.server = None

        # Although server responses will usually be sent via the TCPContext's writer,
        # we create RPC and Event transport objects for uniformity.
        # self.rpc_transport = TCPRPCTransport(self)
        # self.event_transport = TCPEventTransport(self)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        remote_addr = writer.get_extra_info("peername")
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                try:
                    message = json.loads(line.decode())
                except Exception:
                    continue
                pattern = message.get("pattern")
                correlation_id = message.get("correlationId")
                payload = message.get("payload")
                metadata = {
                    "pattern": pattern,
                    "transporter": "tcp",
                    "remote_addr": remote_addr,
                }
                # Create a TCPContext that includes the writer.
                context = TCPContext(
                    correlation_id=correlation_id,
                    is_event=not bool(correlation_id),
                    rpc_transport=TCPRPCTransport(self, writer=writer),
                    event_transport=TCPEventTransport(self, writer=writer),
                    pattern=pattern,
                    remote_addr=str(remote_addr),
                )
                print(message)
                # Pass the received message to the event bus.
                await self.event_bus.emit(context, pattern, payload, metadata)
        except Exception:
            traceback.print_exc()
        finally:
            writer.close()
            await writer.wait_closed()

    async def listen(self):
        """
        Starts the TCP server and listens for incoming connections.
        """
        print("Running server...")
        self.is_stopped = False
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        
        async with self.server:
            await self.server.serve_forever()

    async def close(self):
        """
        Stops the TCP server.
        """
        self.is_stopped = True
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    def unwrap(self, rtype: type[T]) -> T:
        """
        Returns the underlying TCP server instance.
        """
        if not isclass(rtype):
            raise TypeError(f"Unknown transporter instance type {rtype}")
        return self.server  # For example, to inspect server properties.