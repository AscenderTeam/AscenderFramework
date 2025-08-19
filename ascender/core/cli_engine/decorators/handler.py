from typing import Any, Callable, Mapping

from codetiming import Timer

from ascender.core.cli_engine.types.parameter import ParameterInfo
from ..utils.signature_from_callable import _signature_from_callable, _get_parameters


class Handler:
    def __init__(
        self, 
        *names: str, 
        description: str | None = None,
        is_coroutine: bool = False,
        **kwargs
    ) -> None:
        self.names = names
        self.description = description
        self.kwargs = kwargs
        self.is_coroutine = is_coroutine
    
    @Timer("Handler.parse_parameters", text="Elapsed time: {:.2f} ms")
    def parse_parameters(self, f: Callable[..., Any]) -> Mapping[str, ParameterInfo]:
        parameters = _signature_from_callable(f)
        
        return _get_parameters(parameters)
    
    def __call__(self, f: Callable[..., Any]) -> Any:
        f.__metadata__ = self.parse_parameters(f)
        
        return f