import asyncio
from ascender.common.injectable import Injectable
from ascender.common.microservices.instances.bus import SubscriptionEventBus
from ..types.transport import Transport


@Injectable(provided_in=None)
class TransportInstance:
    def __init__(
        self,
        token: str,
        transport: Transport,
        event_bus: SubscriptionEventBus,
        with_client_proxy: bool = False,
    ):
        self.token = token
        self.transport = transport
        self.event_bus = event_bus
        self.with_client_proxy = with_client_proxy
        
        # Initiate transporter
        self.transporter = transport['transport'].value(self, self.event_bus, transport['options'])

    async def startup(self):
        asyncio.create_task(self.transporter.listen())

    async def shutdown(self):
        await self.transporter.close()