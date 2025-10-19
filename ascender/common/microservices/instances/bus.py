import asyncio
import re
from typing import Any, Awaitable, Callable, MutableMapping
import uuid
from ascender.common.injectable import Injectable
from ascender.common.microservices.abc.context import BaseContext
from ascender.common.microservices.abc.event_bus import TransportEventBus
from ascender.common.microservices.types.consumer_metadata import ConsumerMetadata


@Injectable()
class SubscriptionEventBus(TransportEventBus):
    def __init__(self):
        # Token mapping: topic -> { token: callback, ... }
        self._subscriptions: MutableMapping[str, dict[str, Callable[[Any, Any], Awaitable[None]]]] = {}
        self.callbacks: list[Callable[[Any, Any], Awaitable[None]]] = []
    
    async def emit(self, context, topic, data, metadata):
        """
        Emits event data into all subscriptions for current topic

        Args:
            topic (str): Topic of the event
            data (Any): Data of the event
        """
        # List of tasks to execute in parallel
        tasks = []
        
        # Check for wildcards
        for sub_topic, callbacks in self._subscriptions.items():
            if "*" in sub_topic:
                # Convert a pattern like "USER_*" into a regex: ^USER_.*$
                regex_pattern = "^" + re.escape(sub_topic).replace(r"\*", ".*") + "$"
                if re.match(regex_pattern, topic):
                    for callback in callbacks.values():
                        tasks.append(callback(context, data, metadata))
            else:
                if sub_topic == topic:
                    for callback in callbacks.values():
                        tasks.append(callback(context, data, metadata))
        if tasks:
            # Execute all tasks at the same time using `asyncio.gather`
            await asyncio.gather(*tasks, return_exceptions=True)
            tasks = []
    
    def subscribe(self, topic, callback):
        """
        Subscribes to specific types of event

        Args:
            topic (str): Topic where to subscribe
            callback (function): Callback function to invoke during event trigger
        """
        token = uuid.uuid4().hex
        # Check if topic not in subscriptions, if not then just add
        if topic not in self._subscriptions:
            self._subscriptions[topic] = {}
        
        # Add token for topic
        self._subscriptions[topic][token] = callback
        return token
    
    def subscribe_all(self, callback: Callable[[BaseContext, str, Any, ConsumerMetadata], Awaitable[None]]):
        self.callbacks.append(callback)
    
    def unsubscribe(self, topic: str, token: str | None = None):
        """
        Unsubscribes from all events

        Args:
            topic (str): Specific topic to subscribe from
            token (str | None): If needed to unsubscribe from specific token
        """
        if token:
            # Checks if topic & token exist in subscription
            if topic in self._subscriptions and token in self._subscriptions[topic]:
                del self._subscriptions[topic][token]
                if not self._subscriptions[topic]:
                    del self._subscriptions[topic]
        
        else:
            self._subscriptions.pop(topic, None)