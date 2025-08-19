from typing import Annotated, Any, Literal, TypeVar, overload
from typing_extensions import Doc

from ascender.core.cli_engine.types.parameter import ParameterInfo
from ascender.core.cli_engine.types.undefined import UndefinedValue


T = TypeVar("T")


@overload
def Parameter(
    default: T | UndefinedValue | None = UndefinedValue,
) -> T: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = UndefinedValue,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
) -> T: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = UndefinedValue,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
    action: Annotated[Literal["store"] | None, Doc("The action to be taken when the argument is encountered")] = None,
    nargs: Annotated[int | str | None, Doc("Limit the amount number of the arguments to a specific amount.")] = None
) -> T: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = UndefinedValue,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
    action: Annotated[Literal["store_const"] | None, Doc("The action to be taken when the argument is encountered")] = None,
    nargs: Annotated[int | str | None, Doc("Limit the amount number of the arguments to a specific amount.")] = None,
    const: Annotated[str | None, Doc("The default value that will be used for valueless flags.")] = None,
    dest: Annotated[str | None, Doc("The name of the attribute to be used in the application.")] = None,
) -> T: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = UndefinedValue,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
    action: Annotated[Literal["store"] | None, Doc("The action to be taken when the argument is encountered")] = None,
    nargs: Annotated[int | str | None, Doc("Limit the amount number of the arguments to a specific amount.")] = None,
    const: Annotated[str | None, Doc("The default value that will be used for valueless flags.")] = None,
    dest: Annotated[str | None, Doc("The name of the attribute to be used in the application.")] = None,
    metavar: Annotated[str | None, Doc("The name of the argument in the help message.")] = None,
    **kwargs: Any,
) -> T: ...


def Parameter(
    default: Annotated[Any, Doc("The default value for the argument")] = UndefinedValue,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
    action: Annotated[str | None, Doc("The action to be taken when the argument is encountered")] = None,
    nargs: Annotated[int | str | None, Doc("Limit the amount number of the arguments to a specific amount.")] = None,
    const: Annotated[str | None, Doc("The default value that will be used for valueless flags.")] = None,
    dest: Annotated[str | None, Doc("The name of the attribute to be used in the application.")] = None,
    metavar: Annotated[str | None, Doc("The name of the argument in the help message.")] = None,
    **kwargs: Any,
) -> Any:
    """
    A parameter annotation to define a command line parameter for an application.
    This decorator can be used to specify various attributes of the parameter,
    such as its default value, names, description, action, and more.
    """
    
    return ParameterInfo(
        name_or_flags=names,
        default=default,
        help=description,
        action=action,
        nargs=nargs,
        const=const,
        dest=dest,
        metavar=metavar,
        **kwargs,
    )
