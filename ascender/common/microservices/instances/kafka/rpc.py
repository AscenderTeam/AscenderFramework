import asyncio
import json
from logging import Logger
import traceback
from typing import TYPE_CHECKING, Any
from uuid import uuid4
from ascender.common.microservices.abc.rpc_transport import RPCTransport
from reactivex import Subject, operators as ops, throw, timer
from reactivex.scheduler.eventloop import AsyncIOScheduler

from ascender.common.microservices.exceptions.rpc_exception import RPCException
from ascender.common.microservices.instances.kafka.metadata import KafkaMetadata
from ascender.common.microservices.utils.data_parser import decode_message, parse_data
from ascender.common.microservices.utils.defer_mapping import kafka_defer
from ascender.core import inject

if TYPE_CHECKING:
    from ascender.common.microservices.instances.kafka.context import KafkaContext
    from ascender.common.microservices.instances.kafka.transporter import KafkaTransporter
    from ascender.common.microservices.instances.kafka.client import KafkaClient


class KafkaRPCTransport(RPCTransport):

    transport: "KafkaTransporter | KafkaClient"

    def __init__(self, transport: "KafkaTransporter | KafkaClient"):
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

        data = parse_data(data).encode()

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
            ops.map(lambda pair: pair[1])
        ).subscribe(
            on_next=define_response,
            on_error=throw_error
        )

        self.logger.debug(
            f"[yellow] ASCENDER MICROSERVICES [/] | Sending message to [cyan]{pattern}[/] with correlation ID [green]{correlation_id}[/]")
        
        await self.transport.producer.send(topic=pattern, headers=[( "correlationId", correlation_id.encode() )], value=data)
        # INFO LOG
        self.logger.info(
            f"[yellow] ASCENDER MICROSERVICES [/] | Successfully sent message pattern [bold cyan]{pattern}[/] to the message broker")

        # DEBUG LOG
        self.logger.debug(
            f"[yellow] ASCENDER MICROSERVICES [/] | Now waiting for response from message pattern {pattern} from consumer side")

        # Wait for the response
        await response_received.wait()
        # Dispose the subscription after response is received
        subscription.dispose()

        # INFO LOG
        self.logger.info(
            f"[yellow] ASCENDER MICROSERVICES [/] | Received response from consumer message pattern handler {pattern}")

        # Return the response from request
        return await response

    async def send_nack_request(self, pattern, data, timeout):
        """
        Sends request without waiting for response.

        Instead it returns Reactivex observable object with 
        """
        asyncio_scheduler = AsyncIOScheduler(asyncio.get_event_loop())
        correlation_id = str(uuid4())

        data = parse_data(data).encode()

        # Send request
        await self.transport.producer.send(pattern, value=data, headers=[( "correlationId", correlation_id.encode() )])

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
        self.logger.debug(f"[yellow] ASCENDER MICROSERVICES [/] | Requesting consumer side to defer response, and prolong the timeout at the pattern {pattern}")
        await self.transport.producer.send(pattern, value=b"defer", headers=[("correlationId", f"defer-{correlation_id}".encode())])

    async def send_response(self, pattern, correlation_id, response):
        self.logger.debug(
            f"[yellow] ASCENDER MICROSERVICES [/] | Responding to RPC channel using correlation ID {correlation_id} and pattern {pattern}")
        await self.transport.producer.send(pattern, response, headers=[("correlationId", correlation_id.encode())])

    async def raise_exception(self, pattern, correlation_id, exception):
        if not isinstance(exception, RPCException):
            raise TypeError(f"Expected type `RPCException` but got {exception.__class__.__name__}")
        
        await self.transport.producer.send(pattern, json.dumps(exception.to_dict()).encode(), headers=[("correlationId", correlation_id.encode())])

    async def process_response(self, correlation_id, response, **kwargs):
        if not correlation_id:
            return
        
        if not correlation_id.startswith("response-") and not correlation_id.startswith("defer-"):
            return
        
        response = decode_message(response)
        
        if isinstance(response, dict):
            if RPCException.is_exception(response):
                self.response_subject.on_error(RPCException.from_dict(response))
                return
            
        self.response_subject.on_next((correlation_id, decode_message(response), kwargs))

    async def listen_for_requests(self, context: "KafkaContext", data: Any, metadata: KafkaMetadata):
        # print(context, data, metadata)
        if metadata["transporter"] != "kafka":
            return
        await self.process_response(context.correlation_id, data, **metadata)
