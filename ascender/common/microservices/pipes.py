from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Protocol, runtime_checkable

from ascender.common.microservices.abc.context import BaseContext


@runtime_checkable
class PatternPipe(Protocol):
    """Protocol for objects that can transform handler parameter values."""

    async def transform(self, payload: "PipePayload") -> Any:  # pragma: no cover - protocol definition
        ...


@dataclass(slots=True)
class PipePayload:
    """Carries information into pipe functions/classes."""

    raw: Any
    value: Any
    context: BaseContext
    parameter: inspect.Parameter
    parsing_error: Exception | None = None


class PipeMarker:
    """Metadata wrapper used with ``Annotated`` to apply pipes to handler parameters."""

    __slots__ = ("_pipe",)

    def __init__(self, pipe: PatternPipe | type[PatternPipe] | Callable[[PipePayload], Any]):
        if inspect.isclass(pipe):
            self._pipe = pipe()  # type: ignore[call-arg]
        else:
            self._pipe = pipe

    async def run(self, payload: PipePayload) -> Any:
        candidate = self._pipe
        if isinstance(candidate, PatternPipe):
            result = candidate.transform(payload)
        else:
            result = candidate(payload)

        if inspect.isawaitable(result):  # type: ignore[arg-type]
            return await result  # type: ignore[return-value]
        return result


def Pipe(pipe: PatternPipe | type[PatternPipe] | Callable[[PipePayload], Any]) -> PipeMarker:
    """Convenience factory to be used within ``typing.Annotated`` declarations."""

    return PipeMarker(pipe)


__all__ = ["Pipe", "PipeMarker", "PipePayload", "PatternPipe"]
