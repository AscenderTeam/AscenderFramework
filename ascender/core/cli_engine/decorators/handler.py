from typing import Any, Callable, Mapping

from ascender.core.cli_engine.types.handler_metadata import HandlerMetadataInfo_
from ascender.core.cli_engine.types.parameter import ParameterInfo
from ..utils.signature_from_callable import _signature_from_callable, _get_parameters


class Handler:
    def __init__(
        self, 
        *names: str, 
        description: str | None = None,
        **kwargs
    ) -> None:
        """
        `@Handler` decorator's constructor

        Args:
            *names (str): One or more names for the handler.
            description (str | None, optional): A brief description of the handler. Defaults to None.
        """
        self.names = names
        self.description = description
        self.kwargs = kwargs
    
    def parse_parameters(self, f: Callable[..., Any]) -> Mapping[str, ParameterInfo]:
        parameters = _signature_from_callable(f)
        
        return _get_parameters(parameters)
    
    def __call__(self, f: Callable[..., Any]) -> Any:
        f.__metadata__ = HandlerMetadataInfo_(
            _functionname=f.__name__,
            names=list(self.names),
            description=self.description,
            parameters=self.parse_parameters(f),
            additional=self.kwargs,
            docstring=f.__doc__
        )

        return f