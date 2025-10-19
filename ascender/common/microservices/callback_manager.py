import inspect
import json
from logging import Logger
import traceback
from typing import Any, Callable, Optional, Tuple, Type, get_args

from pydantic import BaseModel, ValidationError

from ascender.common import BaseDTO, BaseResponse
from ascender.common.microservices.abc.context import BaseContext
from ascender.common.microservices.exceptions.rpc_exception import RPCException
from ascender.common.microservices.instances.kafka.context import KafkaContext
from ascender.common.microservices.instances.kafka.event import KafkaEventTransport
from ascender.common.microservices.instances.kafka.rpc import KafkaRPCTransport
from ascender.common.microservices.instances.redis.context import RedisContext
from ascender.common.microservices.instances.redis.event import RedisEventTransport
from ascender.common.microservices.instances.redis.rpc import RedisRPCTransport
from ascender.common.microservices.instances.transport import TransportInstance
from ascender.common.microservices.utils.data_parser import parse_data, validate_json, validate_python
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

    def get_context_info(self) -> Optional[Tuple[str, Type[BaseContext]]]:
        """
        Inspects the callback's signature to extract context parameter information.

        It looks for parameters that either use Annotated metadata or have a default value
        with an attribute "context_type". Returns the parameter name and the expected context type.

        :return: A tuple (parameter_name, context_type) if a context parameter is found; otherwise, None.
        """
        for param_name, param in self.callback_signature.parameters.items():
            # Skip typical self/cls parameters.
            if param_name in ("self", "cls"):
                continue
            if param.annotation == inspect._empty:
                continue

            # Check for Annotated metadata.
            if hasattr(param.annotation, "__metadata__"):
                metadata = param.annotation.__metadata__
                if metadata and hasattr(metadata[0], "context_type"):
                    # Return the parameter name and the first argument in Annotated (the actual type)
                    return param_name, get_args(param.annotation)[0]
                continue

            # Fallback: check if the default value has a "context_type" attribute.
            if param.default != inspect._empty and hasattr(param.default, "context_type"):
                return param_name, param.annotation

        return None

    def get_data_field(self) -> Optional[Tuple[str, Any]]:
        """
        Inspects the callback's signature to extract the data parameter information.

        The method skips parameters marked with metadata (assumed to be context parameters)
        and prioritizes parameters whose type is a Pydantic model, DTO, or response type.
        If no Pydantic model is found, it will simply return the first non-context parameter.

        :return: A tuple (parameter_name, parameter_type) representing the data field, or None if not found.
        """
        for param_name, param in self.callback_signature.parameters.items():
            if param_name in ("self", "cls"):
                continue

            # Skip parameters that have metadata (assumed to be reserved for context).
            if hasattr(param.annotation, "__metadata__"):
                continue

            # Check if the parameter is a subclass of a Pydantic model or DTO.
            if isinstance(param.annotation, type) and issubclass(param.annotation, (BaseModel, BaseDTO, BaseResponse)):
                return param_name, param.annotation

            # Otherwise, assume this parameter represents the data.
            return param_name, param.annotation

        return None

    async def handle_rpc_call(self, instance_context: BaseContext, payload: dict[str, Any]) -> None:
        """
        Executes an RPC callback and sends the serialized response.

        :param instance_context: The generated context for the callback.
        :param payload: A dictionary containing the validated payload for the callback.
        """
        instance_context.is_event = False
        try:
            response = await self.callback(**payload)
        except RPCException as e:
            await instance_context.rpc_transport.raise_exception(
                instance_context.pattern,
                f"response-{instance_context.correlation_id}",
                e
            )
            return
        except Exception as e:
            self.logger.error("Unexpected error during RPC call: %s", e)
            raise

        # Serialize the response to JSON and send it using the RPC transport.
        serialized_response = parse_data(response).encode()
        await instance_context.rpc_transport.send_response(
            pattern="_rpc:response",
            correlation_id=f"response-{instance_context.correlation_id}",
            response=serialized_response,
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

        :param metadata: The metadata dictionary from the message broker.
        :return: True if the callback should be ignored; otherwise, False.
        """
        if not context.correlation_id:
            return False

        # Decode the key if it's in bytes.
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

        # Skip processing if the metadata indicates this is a deferred or response message.
        if self._should_ignore(context):
            return

        try:
            payload: dict[str, Any] = {}

            context_info = self.get_context_info()
            data_field_info = self.get_data_field()

            raised_exception = None

            # Validate and assign the data field.
            if data_field_info is not None:
                field_name, field_type = data_field_info
                # Decode if necessary.
                decoded_data = data.decode() if isinstance(data, bytes) else data
                # Handle validation errors
                try:
                    try:
                        payload[field_name] = validate_json(
                            decoded_data, field_type)
                    except ValidationError:
                        payload[field_name] = validate_python(
                            decoded_data, field_type)

                except ValidationError as e:
                    traceback.print_exc()
                    raised_exception = RPCException.from_validation_err(e)

            # Generate and assign the context if the callback expects it.

            if context_info is not None:
                context_field, expected_context_cls = context_info
                # Verify that the generated context matches the expected type.
                if not isinstance(context, expected_context_cls):
                    self.logger.debug(
                        "Skipping callback: Expected context type %s, but message broker provided %s based on metadata type '%s'.",
                        expected_context_cls.__name__,
                        type(context).__name__,
                        metadata.get("transporter", "unknown")
                    )
                    return
                payload[context_field] = context

        except Exception as e:
            self.logger.exception(
                "Error while preparing payload for callback execution: %s", e)
            raise

        # Route to the appropriate handler based on the messaging pattern.
        if not self.is_event:
            if raised_exception:
                # Respond with `RPCException` to the producer
                await context.rpc_transport.raise_exception(
                    context.pattern,
                    f"response-{context.correlation_id}",
                    raised_exception
                )
                return
            await self.handle_rpc_call(context, payload)
        else:
            if raised_exception:
                # Log the exception and continue processing
                self.logger.error(
                    "Error while preparing payload for event execution: %s", raised_exception)
                return
            
            await self.handle_event_call(payload)
