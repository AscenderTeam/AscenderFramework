from ascender.common.microservices.instances.bus import SubscriptionEventBus
from ascender.common.microservices.instances.client_factory import ClientProxyFactory
from ascender.common.microservices.instances.transport import TransportInstance
from ascender.common.microservices.transport_manager import TransportManager
from ascender.common.microservices.types.options import MicroserviceOptions
from ascender.core import Provider
from ascender.core.applications.application import Application
from ascender.core.di.abc.base_injector import Injector


def provideMicroservices(options: list[MicroserviceOptions]) -> list[Provider]:
    transports: list[Provider] = [{
        "provide": f"TRANSPORT_INSTANCE_{t['token']}",
        "use_factory": lambda event_bus, token=t["token"], options=t["options"]: TransportInstance(token, options, event_bus),
        "deps": ["TRANSPORT_EVENTBUS"],
    } for t in options]

    clients: list[Provider] = [{
        "provide": t['token'],
        "use_factory": lambda instance, app: ClientProxyFactory(instance, app).as_provider(),
        "deps": [f"TRANSPORT_INSTANCE_{t['token']}", Application],
    } for t in options if t.get("with_client_proxy", False)]

    return [
        {
            "provide": "TRANSPORT_EVENTBUS",
            "use_class": SubscriptionEventBus
        },
        transports,
        clients,
        {
            "provide": "TRANSPORT_MANAGER",
            "use_factory": lambda application, event_bus, injector: TransportManager(
                application,
                event_bus,
                injector,
                [f"TRANSPORT_INSTANCE_{t['token']}" for t in options]
            ),
            "deps": [Application, "TRANSPORT_EVENTBUS", Injector]
        }
    ]
