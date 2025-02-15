from ascender.common.microservices.abc.context import BaseContext


class RedisContext(BaseContext):
    # Redis-specific field (using channel in place of partition/offset)
    channel: str = ""

    async def send(self, pattern: str, data=None, timeout: float = 10):
        return await self.rpc_transport.send_request(pattern, data, timeout)

    async def send_as_observable(self, pattern: str, data=None, timeout: float = 10):
        return await self.rpc_transport.send_nack_request(pattern, data, timeout)

    async def defer_response(self):
        if self.is_event:
            raise ValueError("Cannot defer response from an event handler!")
        return await self.rpc_transport.defer(self.pattern, self.correlation_id)

    async def emit(self, pattern: str, data=None, **kwargs):
        return await self.event_transport.send_event(pattern, data, **kwargs)

    async def emit_wait(self, pattern: str, data=None, **kwargs):
        return await self.event_transport.send_event_with_defer(pattern, data, **kwargs)