from typing import Any, TypeVar
from ascender.core.di.abc.base_injector import Injector
from ascender.core.di.interface.consts import RAISE_NOT_FOUND
from ascender.core.di.interface.injector import InjectorOptions


T = TypeVar("T")


class NoneInjectorException(Exception):
    """
    None injector exception, in case if there is None value in `Injector`

    Args:
        Exception: Common base class for all non-exit exceptions.
    """

class NoneInjector(Injector):
    """
    None injector instance, in case if there is None value in `Injector`
    """
    def get(
        self,
        token: type[T] | str | Any,
        not_found_value: Any | None = RAISE_NOT_FOUND,
        options: InjectorOptions = {}
    ) -> T | Any | None:
        if not_found_value == RAISE_NOT_FOUND:
            raise NoneInjectorException(f"No provier for {token}!")
        
        if options.get("optional", False):
            return None
        
        return not_found_value