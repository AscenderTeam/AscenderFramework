import asyncio
import json
import traceback
from uuid import uuid4
from reactivex import Subject, operators as ops, throw, timer
from reactivex.scheduler.eventloop import AsyncIOScheduler

from ascender.common.microservices.abc.rpc_transport import RPCTransport
from ascender.common.microservices.exceptions.rpc_exception import RPCException
from ascender.common.microservices.types import AckStatus, RequestType
from ascender.common.microservices.utils.frames import (
    decode_incoming_frame,
    normalize_correlation_id,
    serialize_frame,
)
from ascender.core import inject
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ascender.common.microservices.instances.tcp.context import TCPContext
    from ascender.common.microservices.instances.tcp.transporter import TCPTransporter
    from ascender.common.microservices.instances.tcp.client import TCPClient

class TCPRPCTransport(RPCTransport):
    def __init__(
            self, 
            transport: "TCPTransporter | TCPClient", 
            writer: asyncio.StreamWriter | None = None
        ):
        super().__init__(transport)
        self.response_subject = Subject()
        self.logger = inject("ASC_LOGGER")
        if hasattr(transport, "writer"):
            self.writer = getattr(transport, "writer")
        else:
            self.writer = writer

    def _get_writer(self) -> asyncio.StreamWriter:
        if self.writer is None:
            raise RuntimeError("TCP writer is not configured")
        return self.writer

    async def send_request(self, pattern, data, timeout):
        """
        Sends a request over TCP and waits for the corresponding response.
        """
        loop = asyncio.get_running_loop()
        asyncio_scheduler = AsyncIOScheduler(loop)
        correlation_id = str(uuid4())
        response = asyncio.Future()
        response_received = asyncio.Event()

        frame_payload = serialize_frame(
            request_type=RequestType.CALL,
            payload=data,
            correlation_id=correlation_id,
        )
        envelope = {
            "pattern": pattern,
            "correlationId": correlation_id,
            "payload": frame_payload,
        }
        message = json.dumps(envelope) + "\n"

        def define_response(resp: Any):
            if not response.done():
                response.set_result(resp)
            response_received.set()

        def throw_error(err: Exception):
            if not response.done():
                response.set_exception(err)
            response_received.set()

        subscription = self.response_subject.pipe(
            ops.subscribe_on(asyncio_scheduler),
            ops.timeout(timeout, throw(TimeoutError("Response timed out."))),
            ops.filter(lambda pair: pair[0] == correlation_id),
            ops.first(),
            ops.map(lambda pair: pair[1]),
        ).subscribe(
            on_next=define_response,
            on_error=throw_error,
        )

        self.logger.debug(f"Sending message to {pattern} with correlation ID {correlation_id}")
        
        # Send the message
        writer = self._get_writer()
        writer.write(message.encode())
        await writer.drain()


        self.logger.info(f"Successfully sent message pattern {pattern}")
        self.logger.debug(f"Now waiting for response from pattern {pattern}")

        await response_received.wait()
        subscription.dispose()

        self.logger.info(f"Received response for pattern {pattern}")
        
        return await response

    async def send_nack_request(self, pattern, data, timeout):
        """
        Sends a request without awaiting its response immediately.
        Returns an RxPY observable.
        """
        loop = asyncio.get_running_loop()
        asyncio_scheduler = AsyncIOScheduler(loop)
        correlation_id = str(uuid4())
        frame_payload = serialize_frame(
            request_type=RequestType.CALL,
            payload=data,
            correlation_id=correlation_id,
        )
        envelope = {
            "pattern": pattern,
            "correlationId": correlation_id,
            "payload": frame_payload,
        }
        message = json.dumps(envelope) + "\n"
        writer = self._get_writer()
        writer.write(message.encode())
        await writer.drain()

        observable = self.response_subject.pipe(
            ops.subscribe_on(asyncio_scheduler),
            ops.timeout_with_mapper(
                timer(timeout),
                lambda _: throw(TimeoutError("Response timed out."))
            ),
            ops.filter(lambda pair: pair[0] == correlation_id),
            ops.first(),
            ops.map(lambda pair: pair[1]),
        )
        return observable

    async def send_response(self, pattern, correlation_id, response):
        """
        Sends a response back to the caller.
        (Typically used on the server side via the context's writer.)
        """
        self.logger.debug(f"Responding on pattern {pattern} with correlation ID {correlation_id}")
        frame_payload = serialize_frame(
            request_type=RequestType.ACK,
            payload=response,
            correlation_id=correlation_id,
            ack_status=AckStatus.OK,
        )
        envelope = {
            "correlationId": correlation_id,
            "pattern": pattern,
            "payload": frame_payload,
        }
        message = json.dumps(envelope) + "\n"
        writer = self._get_writer()
        writer.write(message.encode())
        await writer.drain()

    async def raise_exception(self, pattern, correlation_id, exception):
        if not isinstance(exception, RPCException):
            raise TypeError(f"Expected RPCException, got {exception.__class__.__name__}")
        
        frame_payload = serialize_frame(
            request_type=RequestType.ACK,
            payload=exception.to_dict(),
            correlation_id=correlation_id,
            ack_status=AckStatus.ERROR,
        )
        envelope = {
            "correlationId": correlation_id,
            "pattern": pattern,
            "payload": frame_payload,
        }
        message = json.dumps(envelope) + "\n"
        try:
            writer = self._get_writer()
            writer.write(message.encode())
            await writer.drain()
        except:
            traceback.print_exc()

    async def process_response(self, correlation_id, response, **kwargs):
        if not correlation_id:
            return

        frame = decode_incoming_frame(
            response,
            correlation_id=correlation_id,
            default_type=RequestType.ACK,
        )
        normalized_id = normalize_correlation_id(frame.correlation_id)
        if frame.request_type != RequestType.ACK or normalized_id is None:
            return

        metadata = dict(kwargs)
        metadata["ackStatus"] = frame.ack_status

        if frame.ack_status == AckStatus.ERROR:
            if isinstance(frame.payload, dict) and RPCException.is_exception(frame.payload):
                self.response_subject.on_error(RPCException.from_dict(frame.payload))
            else:
                self.response_subject.on_error(RPCException(str(frame.payload)))
            return

        self.response_subject.on_next((normalized_id, frame.payload, metadata))

    async def listen_for_requests(self, context: "TCPContext", data: Any, metadata: dict) -> None:
        """
        For TCP, clients typically do not listen for incoming requests.
        This method is provided for interface compatibility.
        """
        if not context.correlation_id:
            return
        await self.process_response(context.correlation_id, data, **metadata)