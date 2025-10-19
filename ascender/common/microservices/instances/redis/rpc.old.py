import asyncio
import json
from logging import Logger
import traceback
from typing import TYPE_CHECKING, Any
from uuid import uuid4
from ascender.common.microservices.abc.rpc_transport import RPCTransport
from reactivex import Subject, interval, operators as ops, throw, timer, Observable
from reactivex.scheduler.eventloop import AsyncIOScheduler

from ascender.common.microservices.exceptions.rpc_exception import RPCException
from ascender.common.microservices.utils.data_parser import decode_message, parse_data, validate_json
from ascender.common.microservices.utils.defer_mapping import kafka_defer
from ascender.common.microservices.utils.redis_tools import decode_redis_data, parse_redis_encodable
from ascender.core import inject

if TYPE_CHECKING:
    from ascender.common.microservices.instances.transport import TransportInstance


class RedisRPCTransport(RPCTransport):

    def __init__(self, transport):
        super().__init__(transport)
        # A subject to publish all responses.
        self.response_subject = Subject()
        self.logger: Logger = inject("ASC_LOGGER")

    async def send_request(self, pattern, data, timeout):
        """
        Sends request and waits for result.

        Args:
            pattern (str): Topic pattern where to send request.
            data (Any | BaseDTO | BaseResponse | None): JSON-serializable payload.
            timeout (int): Timeout in seconds.

        Raises:
            Exception: If an error occurs on the broker side.

        Returns:
            Any | None: Response object as any type or serialized type.
        """
        loop = asyncio.get_running_loop()  # Updated for Python 3.10+
        asyncio_scheduler = AsyncIOScheduler(loop)
        correlation_id = str(uuid4())
        response = asyncio.Future()  # Use Future for proper async response handling
        response_received = asyncio.Event()

        data = parse_data(data)

        # Subscription to the event response
        def define_response(resp: Any | None):
            """RxPY Callback when response is received."""
            if not response.done():
                response.set_result(resp)  # Properly set response in Future
            response_received.set()  # Allow waiting coroutine to proceed

        def throw_error(err: Exception):
            """Raise an error when RxPY encounters an issue."""
            if not response.done():
                response.set_exception(err)
            response_received.set()

        subscription = self.response_subject.pipe(
            ops.subscribe_on(asyncio_scheduler),
            ops.timeout_with_mapper(timer(timeout), kafka_defer(
                timeout, correlation_id), throw(TimeoutError("Response timed out."))),
            ops.filter(lambda pair: pair[0] == f"response-{correlation_id}"),
            ops.first(),
            ops.map(lambda pair: pair[1]),
        ).subscribe(
            on_next=define_response,
            on_error=throw_error
        )

        self.logger.debug(
            f"[yellow] ASCENDER MICROSERVICES [/] | Sending message to [cyan]{pattern}[/] with correlation ID [green]{correlation_id}[/]")
        subscribers = await self.transport.producer.publish(pattern.encode(), parse_redis_encodable(correlation_id, data))

        # INFO LOG
        self.logger.info(
            f"[yellow] ASCENDER MICROSERVICES [/] | Successfully sent message pattern [bold cyan]{pattern}[/] to the message broker")

        # DEBUG LOG
        self.logger.debug(
            f"Now waiting for response from message pattern {pattern} from consumer side")

        # Wait for the response
        await response_received.wait()
        # Dispose the subscription after response is received
        subscription.dispose()

        # INFO LOG
        self.logger.info(
            f"Received response from consumer message pattern handler {pattern}")

        # Return the response from request
        return await response

    async def send_nack_request(self, pattern, data, timeout):
        """
        Sends request without waiting for response.

        Instead it returns Reactivex observable object with 
        """
        asyncio_scheduler = AsyncIOScheduler(asyncio.get_event_loop())
        correlation_id = str(uuid4())

        data = parse_data(data)

        # Send request
        await self.transport.producer.publish(pattern, parse_redis_encodable(correlation_id, data))

        # Subscribe to the event response
        observable = self.response_subject.pipe(
            ops.subscribe_on(asyncio_scheduler),
            ops.timeout_with_mapper(timer(timeout), kafka_defer(
                timeout, correlation_id), throw(TimeoutError("Response timed out."))),
            ops.filter(lambda pair: pair[0] == f"response-{correlation_id}"),
            ops.first(),
            ops.map(lambda pair: pair[1])
        )

        return observable

    async def defer(
        self,
        pattern: str,
        correlation_id: str
    ):
        """
        Defers the response correlation of the RPC Transport.
        """
        self.logger.debug(
            f"Requesting consumer side to defer response, and prolong the timeout at the pattern {pattern}")
        await self.transport.producer.publish(pattern, parse_redis_encodable(key=f"defer-{correlation_id}"))

    async def send_response(self, pattern, correlation_id, response):
        self.logger.debug(
            f"Responding to RPC channel using correlation ID {correlation_id} and pattern {pattern}")

        await self.transport.producer.publish(pattern, parse_redis_encodable(correlation_id, json.loads(response.decode())))

    async def process_response(self, correlation_id, response, **kwargs):
        if not correlation_id.startswith("response-") and not correlation_id.startswith("defer-"):
            return

        response = decode_message(response)
        if isinstance(response, dict):
            if RPCException.is_exception(response):
                self.response_subject.on_error(RPCException.from_dict(response))
                return

        self.response_subject.on_next((correlation_id, response, kwargs))

    async def raise_exception(self, pattern, correlation_id, exception):
        if not isinstance(exception, RPCException):
            raise TypeError(
                f"Expected type `RPCException` but got {exception.__class__.__name__}")

        await self.transport.producer.publish(pattern, parse_redis_encodable(key=correlation_id, data=exception.to_dict()))

    async def listen_for_requests(self, instance: "TransportInstance", data: bytes, metadata: dict[str, Any]):
        if metadata["type"] != "redis":
            return

        # data = decode_redis_data(data)
        await self.process_response(metadata["key"], data, **metadata)
