from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, field
from typing import Annotated, Any, Sequence, Tuple, get_args, get_origin, get_type_hints

from pydantic import ValidationError

from ascender.common.microservices.abc.context import BaseContext
from ascender.common.microservices.exceptions.rpc_exception import RPCException
from ascender.common.microservices.pipes import PipeMarker, PipePayload
from ascender.common.microservices.types.ctx import CtxMetadata
from ascender.common.microservices.utils.data_parser import validate_json, validate_python


@dataclass(slots=True)
class HandlerParameterPlan:
    parameter: inspect.Parameter
    annotation: Any
    metadata: Tuple[Any, ...]
    is_context: bool
    payload_index: int | None = None
    pipes: Tuple[PipeMarker, ...] = field(default_factory=tuple)

    @property
    def name(self) -> str:
        return self.parameter.name

    @property
    def has_default(self) -> bool:
        return self.parameter.default is not inspect._empty

    @property
    def default(self) -> Any:
        return None if not self.has_default else self.parameter.default

    @property
    def should_parse(self) -> bool:
        return self.annotation is not inspect._empty

    @property
    def has_pipe(self) -> bool:
        return bool(self.pipes)

    @property
    def kind(self) -> inspect._ParameterKind:
        return self.parameter.kind


class HandlerSignaturePlan:
    """Pre-computed representation of a message handler's signature."""

    def __init__(self, callback: Any):
        self.callback = callback
        self.signature = inspect.signature(callback)
        self._annotations = get_type_hints(callback, include_extras=True)
        self.context_params: list[HandlerParameterPlan] = []
        self.payload_params: list[HandlerParameterPlan] = []
        self._analyse()

    def _analyse(self) -> None:
        payload_position = 0
        for name, parameter in self.signature.parameters.items():
            if name in {"self", "cls"}:
                continue

            resolved_annotation = self._annotations.get(name, parameter.annotation)
            annotation, metadata = _unwrap_annotation(resolved_annotation)
            pipes = tuple(meta for meta in metadata if isinstance(meta, PipeMarker))
            is_context = _is_context_parameter(annotation, metadata, parameter)

            plan = HandlerParameterPlan(
                parameter=parameter,
                annotation=annotation,
                metadata=metadata,
                is_context=is_context,
                payload_index=None,
                pipes=pipes,
            )

            if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                raise TypeError("MessagePattern callbacks cannot use *args or **kwargs.")

            if is_context:
                self.context_params.append(plan)
                continue

            plan.payload_index = payload_position
            payload_position += 1
            self.payload_params.append(plan)

    def _decode_data(self, data: Any) -> Any:
        if isinstance(data, bytes):
            try:
                data = data.decode()
            except UnicodeDecodeError:
                data = data.decode(errors="ignore")
        if isinstance(data, str):
            stripped = data.strip()
            if not stripped:
                return ""
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return data

    def _extract_raw(self, payload: Any, plan: HandlerParameterPlan) -> tuple[Any, bool]:
        if payload is None:
            return None, False
        if isinstance(payload, dict):
            if plan.name in payload:
                return payload[plan.name], True
            return None, False
        if isinstance(payload, (list, tuple)):
            if plan.payload_index is None:
                return None, False
            if 0 <= plan.payload_index < len(payload):
                return payload[plan.payload_index], True
            return None, False
        # Single parameter receives the whole payload
        if len(self.payload_params) == 1:
            return payload, True
        return None, False

    async def resolve_payload(self, context: BaseContext, data: Any) -> dict[str, Any]:
        decoded = self._decode_data(data)
        payload: dict[str, Any] = {}
        for plan in self.context_params:
            payload[plan.name] = context

        if not self.payload_params:
            return payload

        for plan in self.payload_params:
            raw_value, found = self._extract_raw(decoded, plan)
            if not found:
                if plan.has_default:
                    payload[plan.name] = plan.default
                    continue
                raise RPCException(
                    message=f"Missing required payload field '{plan.name}'",
                    code=400,
                )

            parsed_value, parse_error = raw_value, None
            if plan.should_parse:
                parsed_value, parse_error = self._attempt_parse(raw_value, plan)

            if plan.has_pipe:
                current_value = parsed_value if parse_error is None else raw_value
                for marker in plan.pipes:
                    pipe_payload = PipePayload(
                        raw=raw_value,
                        value=current_value,
                        context=context,
                        parameter=plan.parameter,
                        parsing_error=parse_error,
                    )
                    current_value = await marker.run(pipe_payload)
                payload[plan.name] = current_value
                continue

            if parse_error:
                if isinstance(parse_error, ValidationError):
                    raise RPCException.from_validation_err(parse_error)
                raise RPCException(str(parse_error), code=400)

            payload[plan.name] = parsed_value

        return payload

    def _attempt_parse(self, raw_value: Any, plan: HandlerParameterPlan) -> tuple[Any, Exception | None]:
        if not plan.should_parse:
            return raw_value, None

        prepared = raw_value
        if isinstance(raw_value, bytes):
            prepared = raw_value.decode()

        # Strings can be json-encoded payloads, try json first
        if isinstance(prepared, str):
            try:
                return validate_json(prepared, plan.annotation), None
            except ValidationError as err:
                last_error: Exception = err
            else:
                last_error = None
            try:
                return validate_python(prepared, plan.annotation), None
            except ValidationError as err:
                last_error = err
            return None, last_error

        try:
            return validate_python(prepared, plan.annotation), None
        except ValidationError as err:
            return None, err


def _unwrap_annotation(annotation: Any) -> tuple[Any, Tuple[Any, ...]]:
    metadata: Tuple[Any, ...] = tuple()
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        if not args:
            return annotation, metadata
        return args[0], tuple(args[1:])
    return annotation, metadata


def _is_context_parameter(annotation: Any, metadata: Sequence[Any], parameter: inspect.Parameter) -> bool:
    for meta in metadata:
        if getattr(meta, "context_type", False):
            return True
    if parameter.default is not inspect._empty and getattr(parameter.default, "context_type", False):
        return True
    if inspect.isclass(annotation) and issubclass(annotation, BaseContext):
        return True
    return False
