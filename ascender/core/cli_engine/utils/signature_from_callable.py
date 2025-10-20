import inspect

from typing import Any, Callable, Mapping, Sequence
from typing_extensions import Doc

from ascender.core.cli_engine.types.parameter import ParameterInfo


def _signature_from_callable(callable: Callable[..., Any]) -> Mapping[str, inspect.Parameter]:
    signature = inspect.signature(callable)
    
    return signature.parameters


def _inspect_annotated(annotation: Any) -> Sequence[ParameterInfo | Any] | None:
    if hasattr(annotation, "__metadata__"):
        return annotation.__metadata__


def _get_parameters(parameters: Mapping[str, inspect.Parameter]) -> Mapping[str, ParameterInfo]:
    param_infos: dict[str, ParameterInfo] = {}
    qual = callable.__qualname__
    inside_class = "." in qual and not qual.endswith(".<locals>")

    
    for name, parameter in parameters.items():
        
        if name == "self" or name == "cls":
            continue

        default = parameter.default
        annotation = parameter.annotation
        
        # check if parameter's default is empty
        default_empty = default is inspect._empty
        
        # avoid self-reflective attributes and don't raise a type error to them.
        if inside_class and name in ("self", "cls"):
            continue
        
        if parameter.kind == inspect._ParameterKind.POSITIONAL_ONLY:
            raise TypeError(f"Parameter {name!r} in {callable.__qualname__} is positional-only, " \
                            "which Ascender CLI does not support. Use normal args instead.")
        
        if default_empty:
            # Python 3.9 < support, we ensure that we handled types using Annotated[..., Paramter(...)]
            if hasattr(annotation, "__metadata__"):
                _annotation = _inspect_annotated(parameter.annotation)
                
                if _annotation is not None:
                    default = _annotation[0]
        
        if isinstance(default, ParameterInfo):
            # Assign annotation to ParameterInfo just to validate it during evaluation
            default.annotation = annotation
            param_infos[name] = default
            continue
        
        _help: str | None = None
        
        # In case if `Annotated[..., Doc(...)]` was passed, use it in help usage.
        if isinstance(default, Doc):
            _help = default.documentation
        
        if not default_empty:
            instance = ParameterInfo(name, dest=name, action="store", help=_help)
            instance.annotation = annotation
            param_infos[name] = instance
            continue
        
        instance = ParameterInfo(name, dest=name, action="store", help=_help)
        instance.annotation = annotation
        param_infos[name] = instance
    
    return param_infos