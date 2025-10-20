from typing import Annotated, Any, Callable, Literal, TypeVar, overload
from typing_extensions import Doc

from ascender.core.cli_engine.types.parameter import ParameterInfo
from ascender.core.cli_engine.types.undefined import UndefinedValue


T = TypeVar("T")


@overload
def Parameter(
    default: T | UndefinedValue | None = ...,
) -> T | Any: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = ...,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
) -> T | Any: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = ...,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
    action: Annotated[Literal["store"] | None, Doc("The action to be taken when the argument is encountered")] = None,
    nargs: Annotated[int | str | None, Doc("Limit the amount number of the arguments to a specific amount.")] = None
) -> T | Any: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = ...,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
    action: Annotated[Literal["store_const"] | None, Doc("The action to be taken when the argument is encountered")] = None,
    nargs: Annotated[int | str | None, Doc("Limit the amount number of the arguments to a specific amount.")] = None,
    const: Annotated[str | None, Doc("The default value that will be used for valueless flags.")] = None,
    dest: Annotated[str | None, Doc("The name of the attribute to be used in the application.")] = None,
) -> T | Any: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = ...,
    *,
    default_factory: Annotated[Callable[[], T] | None, Doc("A callable that returns the default value for the argument")] = ...,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
    action: Annotated[Literal["store_const"] | None, Doc("The action to be taken when the argument is encountered")] = None,
    nargs: Annotated[int | str | None, Doc("Limit the amount number of the arguments to a specific amount.")] = None,
    const: Annotated[str | None, Doc("The default value that will be used for valueless flags.")] = None,
    dest: Annotated[str | None, Doc("The name of the attribute to be used in the application.")] = None,
) -> T | Any: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = ...,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
    action: Annotated[Literal["store"] | None, Doc("The action to be taken when the argument is encountered")] = None,
    nargs: Annotated[int | str | None, Doc("Limit the amount number of the arguments to a specific amount.")] = None,
    const: Annotated[str | None, Doc("The default value that will be used for valueless flags.")] = None,
    dest: Annotated[str | None, Doc("The name of the attribute to be used in the application.")] = None,
    metavar: Annotated[str | None, Doc("The name of the argument in the help message.")] = None,
    **kwargs: Any,
) -> T | Any: ...


@overload
def Parameter(
    default: T | UndefinedValue | None = ...,
    *,
    names: list[str] | None = None,
    description: Annotated[str | None, Doc("A brief description of the argument (used for help)")] = None,
    action: Annotated[Literal["append", "extend"] | None, Doc("The action to be taken when the argument is encountered")] = None,
    nargs: Annotated[int | str | None, Doc("Limit the amount number of the arguments to a specific amount.")] = None,
    const: Annotated[str | None, Doc("The default value that will be used for valueless flags.")] = None,
    dest: Annotated[str | None, Doc("The name of the attribute to be used in the application.")] = None,
    metavar: Annotated[str | None, Doc("The name of the argument in the help message.")] = None,
    **kwargs: Any,
) -> T | Any: ...


def Parameter(
    default: Annotated[Any, Doc("The default value for the argument")] = UndefinedValue,
    *,
    default_factory: Annotated[Callable[[], T] | None, Doc("A callable that returns the default value for the argument")] = None,
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
    
    Args:
        default: The default value for the argument.
        default_factory: A callable that returns the default value for the argument.
        names: A list of names or flags for the argument.
        description: A brief description of the argument (used for help).
        action: The action to be taken when the argument is encountered.
        nargs: Limit the amount number of the arguments to a specific amount.
        const: The default value that will be used for valueless flags.
        dest: The name of the attribute to be used in the application.
        metavar: The name of the argument in the help message.
        **kwargs: Additional keyword arguments for further customization.
    """
    return ParameterInfo(
        name_or_flags=names,
        default=default,
        default_factory=default_factory,
        help=description,
        action=action,
        nargs=nargs,
        const=const,
        dest=dest,
        metavar=metavar,
        **kwargs,
    )
