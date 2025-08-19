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
    specified: bool = False,
    description: str | None = None,
    flags: list[str] | None = None,
) -> bool: ...


def BooleanParameter(
    default: bool = False,
    *,
    specified: bool = False,
    description: str | None = None,
    flags: list[str] | None = None,
) -> Any:
    """
    Create a boolean flag parameter for the CLI engine.
    If CLI will get value as `--flag` it will be set to `True`, otherwise it will be set to `False`.
    
    Parameters
    ----------
    default : bool, optional
        Default value of boolean parameter, by default False
    description : str | None, optional
        Description of the parameter, by default None
    specified : bool, optional
        If True, the parameter is considered specified and will be set to True when the flag is
        encountered, by default False
    flags : list[str] | None, optional
        List of flags that will be used to trigger this parameter, by default None.
        If None, the parameter will not have any flags and will not be triggered by CLI.
        If provided, each flag must start with '--' or '-'.
    """
    
    for flag in flags or []:
        if not flag.startswith("--") or not flag.startswith("-"):
            raise ValueError(f"Flag '{flag}' must start with '--'.")
    
    return ParameterInfo(
        name_or_flags=flags,
        default=default,
        description=description,
        action="store_true" if specified else "store_false",
    )