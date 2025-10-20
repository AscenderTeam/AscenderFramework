from typing import Any, TypeVar, overload

from ascender.core.cli_engine.types.parameter import ParameterInfo
from ascender.core.cli_engine.types.undefined import UndefinedValue


T = TypeVar("T")


@overload
def ConstantParameter(
    const: Any,
    default: T | None = UndefinedValue,
) -> T: ...


@overload
def ConstantParameter(
    const: Any,
    default: T | None = UndefinedValue,
    *,
    description: str | None = None,
    flags: list[str] | None = None,
    dest: str | None = None,
    metavar: str | None = None,
) -> T: ...


def ConstantParameter(
    const: Any,
    default: Any | None = UndefinedValue,
    *,
    description: str | None = None,
    flags: list[str] | None = None,
    dest: str | None = None,
    metavar: str | None = None,
) -> Any:
    """
    Create a boolean flag parameter for the CLI engine.
    If CLI will get value as `--flag` it will be set to `True`, otherwise it will be set to `False`.
    
    Args:
        const (Any): The constant value to be used when the flag is provided.
        default (Any | None, optional): The default value if the flag is not provided. Defaults to UndefinedValue.
        description (str | None, optional): A brief description of the argument (used for help). Defaults to None.
        flags (list[str] | None, optional): One or more flag names (e.g., ["--my-flag"]). Defaults to None.
        dest (str | None, optional): The name of the attribute to be used in the application. Defaults to None.
        metavar (str | None, optional): The name to be used in usage messages. Defaults to None.
    """
    
    for flag in flags or []:
        if not flag.startswith("--") or not flag.startswith("-"):
            raise ValueError(f"Flag '{flag}' must start with '--'.")
    
    return ParameterInfo(
        name_or_flags=flags,
        default=default,
        description=description,
        action="store_const",
        const=const,
        dest=dest,
        metavar=metavar or dest or "CONSTANT",
    )