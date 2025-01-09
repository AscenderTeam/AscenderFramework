import inspect
from typing import Any, Callable, MutableMapping, get_type_hints

from ascender.core.di.interface.injection_metadata import InjectionMetadata


def injection_def(constructor: Callable[..., None]):
    """
    Gets injection signature (metadata) of injectable and return injection tokens

    Args:
        constructor (Callable[..., None]): Constructor object, usually `__init__` function. But can be any
    """
    signature = inspect.signature(constructor)
    params = signature.parameters

    injection_tokens: MutableMapping[str, type[Any] | str] = {}

    for name, param in params.items():
        if name == "self":
            continue
        # NOTE Annotations are strictly REQUIRED in injectable function, if there are no type safe annotation, raise an error
        if param.annotation == inspect._empty:
            raise TypeError(f"Failed to resolve an injectable token for not annotated parameter {param} of callable {constructor.__name__}")
        
        # Type hints of the function
        # NOTE: We use it to handle Annotated and metadata parameters

        # If current parameter uses parameter: Annotated[(type), Inject((token))] from typing and `ascender.core.di`
        if hasattr(param.annotation, "__metadata__"):
            metadata = param.annotation.__metadata__[0]
            
            # Returns token of injectable
            if isinstance(metadata, InjectionMetadata):
                injection_tokens[name] = metadata.token
                continue
        
        # Fallback to parameter annotation
        injection_tokens[name] = param.annotation
    
    return injection_tokens