from typing import Annotated, Any, overload

from ascender.core.cli_engine.types.parameter import ParameterInfo


@overload
def BooleanParameter(
    default: bool = False,
) -> bool: ...


@overload
def BooleanParameter(
    default: bool = False,
    *,
    description: str | None = None,
    flags: list[str] | None = None,
) -> bool: ...


def BooleanParameter(
    default: bool = False,
    *,
    description: str | None = None,
    flags: list[str] | None = None,
) -> Any:
    """
    Create a boolean flag parameter for the CLI engine.
    
    Args:
        default (bool, optional): The default value for the boolean flag. Defaults to False.
        description (str | None, optional): A brief description of the flag (used for help
        messages). Defaults to None.
        flags (list[str] | None, optional): A list of flag names (e.g., ["--verbose", "-v"]).
        Defaults to None.
    """
    
    # Validate flags
    for flag in flags or []:
        if not (flag.startswith("--") or flag.startswith("-")):
            raise ValueError(f"Flag '{flag}' must start with '--' or '-'.")
    
    # Determine action based on default value
    action = "store_true" if not default else "store_false"
    
    return ParameterInfo(
        name_or_flags=flags,
        default=default,
        help=description,
        action=action,
    )