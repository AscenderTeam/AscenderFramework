import asyncio
from inspect import isclass
import json
import traceback
from typing import Any, TypeVar
from ascender.common.microservices.abc.client_proxy import ClientProxy, Undefined
from ascender.common.microservices.instances.tcp.context import TCPContext
from ascender.common.microservices.instances.tcp.event import TCPEventTransport
from ascender.common.microservices.instances.tcp.rpc import TCPRPCTransport
from ascender.common.microservices.utils.data_parser import validate_python
from reactivex import operators as ops

T = TypeVar("T")

class TCPClient(ClientProxy):
    def __init__(self, event_bus, configs: dict = {}, instance=None):
        super().__init__(event_bus, configs, instance)
        self.host = self.configs.get("host", "127.0.0.1")
        self.port = self.configs.get("port", 8888)

        if instance is not None:
            raise ValueError("TCP transport doesn't support initiating with client proxy!")

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self.rpc_transport = TCPRPCTransport(self)
        self.event_transport = TCPEventTransport(self)

        asyncio.create_task(self.run_reader())
    
    async def run_reader(self):
        try:
            while True:
                line = await self.reader.readline()
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
                    "remote_addr": self.host,
                }
                # Create a TCPContext that includes the writer.
                context = TCPContext(
                    correlation_id=correlation_id,
                    is_event=not bool(correlation_id),
                    rpc_transport=TCPRPCTransport(self),
                    event_transport=TCPEventTransport(self),
                    pattern=pattern,
                    remote_addr=self.host,
                )
                # Pass the received message to the event bus.
                await self.event_bus.emit(context, pattern, payload, metadata)
        except Exception:
            traceback.print_exc()
        finally:
            self.writer.close()
            await self.writer.wait_closed()

    async def disconnect(self):
        if self.instance:
            return
        
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def send(self, pattern: str, data: Any = None, timeout: float = 20.0,
                   response_type: type[T] = Any):
        response = await self.rpc_transport.send_request(pattern=pattern, data=data, timeout=timeout)
        return validate_python(response, response_type)

    async def send_as_observable(self, pattern: str, data: Any = None, timeout: float = 20.0,
                                 response_type: type[T] = Any):
        observable = await self.rpc_transport.send_nack_request(pattern=pattern, data=data, timeout=timeout)
        return observable.pipe(
            ops.map(lambda res: validate_python(res, response_type))
        )

    async def emit(self, pattern: str, data: Any = None, **kwargs):
        return await self.event_transport.send_event(pattern=pattern, data=data, **kwargs)

    def unwrap(self, rtype: type[T]) -> T:
        if not isclass(rtype):
            raise TypeError(f"Unknown transporter instance type {rtype}")
        # For TCP, for example, we can unwrap and return the underlying writer.
        if rtype.__name__ == "StreamWriter":
            return self.writer
        raise TypeError(f"Unknown transporter instance type {rtype.__name__}")