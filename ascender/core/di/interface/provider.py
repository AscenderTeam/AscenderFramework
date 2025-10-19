from typing import Any, Callable, ForwardRef, NotRequired, TypeVar
from typing_extensions import TypedDict


class ValueProvider(TypedDict):
    """
    Configures `AscenderInjector` to handle initiated value of specified `type` and uses it's `type` as Injectable Token.

    It will return value specified in `value` for a token as it's type `type(value)`
    """
    provide: type[Any] | str
    """
    An injection token
    """
    
    value: Any
    """
    Value of Value Provider
    """

    multi: NotRequired[bool]
    """
    When set True, it will return a list of instances. Useful for multiple providers
    """


class StaticClassProvider(TypedDict):
    """
    Configures `AscenderInjector` to return an instance of `use_class` for a token
    """
    
    use_class: NotRequired[type[Any]]
    """
    Class to instantiate for the `token`. By default it will taken from `type` of `provide`
    """
    
    provide: type[Any] | str
    """
    An injection token
    """

    multi: NotRequired[bool]
    """
    When set True, it will return a list of instances. Useful for multiple providers
    """

    deps: NotRequired[list[Any]]
    """
    A list of token to be resolved by the injector
    """


class FactoryProvider(TypedDict):
    """
    Configures the `AscenderInjector` to return a value by invoking a `use_factory` callable
    """
    
    provide: type[Any] | str
    """
    An injection token, (use instance of `type` or anything)
    """

    use_factory: Callable[..., Any]
    """
    A function to invoke and to create a value for this. The function will be invoked with resolved values to this `token`
    """

    multi: NotRequired[bool]
    """
    When set True, it will return a list of instances. Useful for multiple providers
    """
    
    deps: NotRequired[list[Any]]
    """
    A list of tokens to be resolved by the injector
    """


TypeProvider = TypeVar("TypeProvider", bound=type[Any])
"""
Classic and default configuration.
Creates an instance by invoking `__init__` method of `type`.

Uses specified `type` as an injectable `token`
"""

Provider = (ValueProvider 
            | StaticClassProvider 
            | FactoryProvider 
            | type[Any]
            | Any)