import asyncio
from typing import Callable

from ascender.common.microservices.callback_manager import CallbackManager
from ascender.common.microservices.instances.bus import SubscriptionEventBus
from ascender.common.microservices.instances.transport import TransportInstance
from ascender.core.applications.application import Application

from ascender.core.di.abc.base_injector import Injector


class TransportManager:
    def __init__(
        self, 
        application: Application,
        event_bus: SubscriptionEventBus,
        injector: Injector,
        transports: list[str],
    ):
        self.application = application
        self.event_bus = event_bus
        self.injector = injector
        self.transport_instances = transports
        self.working_instances: list[TransportInstance] = []

        self.application.app.add_event_handler("startup", self.on_bootstrap)
        self.application.app.add_event_handler("shutdown", self.on_shutdown)

    async def on_bootstrap(self):
        instances_init = []
        for token in self.transport_instances:
            instance: TransportInstance = self.injector.get(token)

            instances_init.append(instance.startup())
            self.working_instances.append(instance)
        
        if instances_init:
            await asyncio.gather(*instances_init)

    async def on_shutdown(self):
        instances_shutdown = []
        for instance in self.working_instances:
            instances_shutdown.append(instance.shutdown())
        
        if instances_shutdown:
            await asyncio.gather(*instances_shutdown)
    
    def add_message_pattern(
        self, 
        pattern: str, 
        callback: Callable
    ):
        self.event_bus.subscribe(pattern, CallbackManager(False, callback))
    
    def add_event_pattern(
        self,
        pattern: str,
        callback: Callable
    ):
        self.event_bus.subscribe(pattern, CallbackManager(True, callback))