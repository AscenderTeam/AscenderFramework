from typing import Any
from ascender.common.microservices.abc.client_proxy import ClientProxy
from ascender.common.microservices.instances.transport import TransportInstance
from ascender.common.microservices.types.transport import TRANSPORT_PROXY_MAPPING, Transports
from ascender.core.applications.application import Application
from ascender.core.di.injectfn import inject


class ClientProxyFactory:
    def __init__(
        self, 
        instance: TransportInstance,
        application: Application
    ):
        self.instance = instance
        self.application = application

    def as_provider(self):
        proxy_instance = TRANSPORT_PROXY_MAPPING[self.instance.transport["transport"].value]
        instance = proxy_instance(self.instance.event_bus, self.instance.transport["options"], self.instance)
        self.application.app.add_event_handler("startup", instance.connect)
        self.application.app.add_event_handler("shutdown", instance.disconnect)
        return instance
    
    @staticmethod
    def create(
        transport: Transports | type[ClientProxy],
        options: dict[str, Any] = {}
    ) -> ClientProxy:
        event_bus = inject("TRANSPORT_EVENTBUS")
        application = inject(Application)

        if isinstance(transport, Transports):
            proxy_instance = TRANSPORT_PROXY_MAPPING[transport.value](event_bus, options)
        
        else:
            proxy_instance = transport(event_bus, options)
        
        application.app.add_event_handler("startup", proxy_instance.connect)
        
        # Add shutdown event handler to disconnect from instance
        application.app.add_event_handler("shutdown", proxy_instance.disconnect)

        return proxy_instance
    
    @staticmethod
    async def acreate(
        transport: Transports | type[ClientProxy],
        options: dict[str, Any] = {}
    ) -> ClientProxy:
        event_bus = inject("TRANSPORT_EVENTBUS")
        application = inject(Application)

        if isinstance(transport, Transports):
            proxy_instance = TRANSPORT_PROXY_MAPPING[transport.value](event_bus, options)
        
        else:
            proxy_instance = transport(event_bus, options)
        
        await proxy_instance.connect()
        
        # Add shutdown event handler to disconnect from instance
        application.app.add_event_handler("shutdown", proxy_instance.disconnect)

        return proxy_instance