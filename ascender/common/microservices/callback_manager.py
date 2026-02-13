import inspect
from logging import Logger
from typing import Any, Callable

from ascender.common.microservices.abc.context import BaseContext
from ascender.common.microservices.exceptions.rpc_exception import RPCException
from ascender.common.microservices.types import RequestType
from ascender.common.microservices.utils.frames import decode_incoming_frame
from ascender.common.microservices.utils.handler_signature import HandlerSignaturePlan
from ascender.core import inject


class CallbackManager:
    """
    Manages the execution of callbacks for various message brokers (e.g. Kafka, Redis).

    This class inspects the callback function's signature to determine the expected
    parameters (context and data) and orchestrates the call with a validated payload.
    It supports both event-based and RPC-based messaging patterns.

    Future brokers can be added by extending the generate_context() method.
    """

    def __init__(self, is_event: bool, callback: Callable[..., Any]) -> None:
        """
        Initialize the CallbackManager.

        :param is_event: If True, the callback is an event handler; if False, it is an RPC handler.
        :param callback: The callable to execute when a message is received.
        """
        self.is_event = is_event
        self.callback = callback
        self.callback_signature = inspect.signature(callback)
        self.logger: Logger = inject("ASC_LOGGER")
        self.signature_plan = HandlerSignaturePlan(callback)

    async def handle_rpc_call(self, instance_context: BaseContext, payload: dict[str, Any]) -> None:
        """
        Executes an RPC callback and sends the serialized response.

        :param instance_context: The generated context for the callback.
        :param payload: A dictionary containing the validated payload for the callback.
        """
        instance_context.is_event = False
        if instance_context.correlation_id is None:
            raise ValueError("RPC calls must include a correlation id")

        try:
            response = await self.callback(**payload)
        except RPCException as exc:
            await instance_context.rpc_transport.raise_exception(
                pattern="_rpc:response",
                correlation_id=instance_context.correlation_id,
                exception=exc,
            )
            return
        except Exception as exc:
            self.logger.exception("Unexpected error during RPC call: %s", exc)
            await instance_context.rpc_transport.raise_exception(
                pattern="_rpc:response",
                correlation_id=instance_context.correlation_id,
                exception=RPCException(str(exc), code=500),
            )
            return

        await instance_context.rpc_transport.send_response(
            pattern="_rpc:response",
            correlation_id=instance_context.correlation_id,
            response=response,
        )

    async def handle_event_call(self, payload: dict[str, Any]) -> None:
        """
        Executes an event callback.

        :param payload: A dictionary containing the validated payload for the callback.
        """
        try:
            await self.callback(**payload)
        except Exception as e:
            self.logger.error("Unexpected error during event call: %s", e)
            raise

    def _should_ignore(self, context: BaseContext) -> bool:
        """
        Determines whether the callback execution should be skipped based on metadata.

        If the "key" in metadata starts with "defer-" or "response-", the callback will not be executed.

        This method remains for backwards compatibility while the new frame model
        is being fully rolled out across transports.
        """
        if not context.correlation_id:
            return False

        return context.correlation_id.startswith("defer-") or context.correlation_id.startswith("response-")

    async def __call__(self, context: BaseContext, data: Any, metadata: dict[str, Any]) -> None:
        """
        Prepares the payload and executes the callback based on the messaging pattern.

        This method:
          1. Checks whether the callback should be skipped.
          2. Extracts and validates the data payload.
          3. Generates the context (if required) using metadata (which must include the "type" key).
          4. If a context parameter is declared, ensures that the generated context matches the expected
             type. If not, the callback is ignored.
          5. Delegates the callback to either the RPC or event handler.

        :param instance: The transport instance used to build the context.
        :param data: The raw data received from the message broker.
        :param metadata: Metadata associated with the message (must include a "type" key).
        :raises ValueError: If an RPC callback is missing its required context.
        """
        self.logger.debug("Executing callback: %s", self.callback)

        frame = decode_incoming_frame(
            data,
            correlation_id=context.correlation_id,
            default_type=RequestType.EVENT if self.is_event else RequestType.CALL,
        )

        if frame.request_type == RequestType.ACK:
            self.logger.debug("Ignoring ACK frame for pattern %s", context.pattern)
            return

        if self._should_ignore(context):
            return

        try:
            payload = await self.signature_plan.resolve_payload(context, frame.payload)
        except RPCException as exc:
            if not self.is_event and context.correlation_id:
                await context.rpc_transport.raise_exception(
                    pattern="_rpc:response",
                    correlation_id=context.correlation_id,
                    exception=exc,
                )
            else:
                self.logger.error("RPC validation error for event %s: %s", context.pattern, exc)
            return
        except Exception as exc:
            self.logger.exception("Error while preparing payload for callback execution: %s", exc)
            if not self.is_event and context.correlation_id:
                await context.rpc_transport.raise_exception(
                    pattern="_rpc:response",
                    correlation_id=context.correlation_id,
                    exception=RPCException(str(exc), code=500),
                )
            return

        if not self.is_event:
            await self.handle_rpc_call(context, payload)
        else:
            await self.handle_event_call(payload)
