from typing import Any, ForwardRef, cast

from ascender.core.di.utils.providers import is_type_provider
from ..interface.provider import Provider


def is_forward_ref(token: Any) -> bool:
    """
    Determines if a token is a forward reference.

    Args:
        token (Any): The token to check.

    Returns:
        bool: True if the token is a forward reference, False otherwise.
    """
    return isinstance(token, (str, ForwardRef))


def resolve_dep_forward_ref(token: str | ForwardRef, records: list[type[Any]]) -> type[Any]:
    """
    Resolves dependency forward reference using Dependency records of `AscenderInjector`

    Args:
        token (str | ForwardRef): Token which required by dependency
        records (list[type[Any]]): Dependency records of `AscenderInjector`

    Raises:
        TypeError: If token was not found in records, in AscenderInjector it should cause `NoneInjector` (NullInjector) error
        TypeError: If token is not string or forward reference.

    Returns:
        type[Any]: Type object of dependency
    """
    records_map = {record.__name__: record for record in records}

    if isinstance(token, ForwardRef):
        resolved_name = token.__forward_arg__
    elif isinstance(token, str):
        resolved_name = token
    else:
        raise TypeError(f"Token should be either a forward reference or string, but got {type(token)}")
    
    # Resolve the token from the records map
    resolved_type = records_map.get(resolved_name)

    if resolved_type is None:
        raise TypeError(f"Token '{resolved_name}' not found in records!")
    
    return resolved_type


def resolve_forward_ref(token: str | type[Any] | ForwardRef, globalns: dict[str, Any] | None = None, localns: dict[str, Any] | None = None) -> type[Any] | str:
    """
    Resolvs forward reference for token.
    If the token is direct type, then it will return it as a direct type

    Args:
        token (str | type[Any] | ForwardRef): Token which can be either direct type, forward reference or string typed forward reference
        globalns (dict[str, Any] | None, optional): The global namespace for resolving forward references. Defaults to None.
        localns (dict[str, Any] | None, optional): The local namespace for resolving forward references. Defaults to None.

    Raises:
        ValueError: Cannot resolve forward reference.
        ValueError: Unsupported token type.

    Returns:
        type[Any]: The resolved token.
    """
    globalns = globalns or globals()
    localns = localns or locals()

    if is_forward_ref(token):
        # Handle forward ref
        try:
            if isinstance(token, ForwardRef):
                resolved = token._evaluate(globalns, localns)  # type: ignore | Resolve ForwardRef 
            else:  # Assume string-based forward reference
                resolved = eval(token, globalns, localns) # type: ignore
            return cast(type[Any], resolved)
        except Exception as e:
            print(e)
            return str(token)
    
    elif isinstance(token, type):
        return token
    
    else:
        # Raise error for unsupported cases
        raise ValueError(f"Unsupported token type: {type(token)} - {token}")