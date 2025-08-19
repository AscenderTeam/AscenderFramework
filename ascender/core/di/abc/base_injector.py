from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar, overload

from ascender.core.di.interface.consts import RAISE_NOT_FOUND
from ascender.core.di.interface.injector import InjectorOptions

from ..interface.provider import Provider


T = TypeVar("T")


class Injector(ABC):
    
    @overload
    def get(
        self,
        token: type[T],
        not_found_value: Any | None = RAISE_NOT_FOUND,
        options: InjectorOptions = {
            "optional": False
        }
    ) -> T | Any | None:
        """
        Resolves and gets dependency by `token`

        Args:
            token (type[T]): An injection token used to find injectable to return
            not_found_value (Any | None, optional): Value which will be returned if not found. Defaults to None.
            options (_type_, optional): Injector configuration. Defaults to { "optional": False }.

        Returns:
            T: An object resolved to `token`
            Any: In case if unable to resolve, token not found and `not_found_value` set to type other then `None`
            None: In case if unable to resolve dependency, token not found and `not_found_value` set to `None`
        """
        ...

    @overload
    def get(
        self,
        token: str | Any,
        not_found_value: Any | None = RAISE_NOT_FOUND,
        options: InjectorOptions = {
            "optional": False
        }
    ) -> Any | None:
        """
        Resolves and gets dependency by `token` specifically as other type then `type` instance or it's passed as a forward reference

        Args:
            token (str | Any): An injection token used to find injectable to return
            not_found_value (Any | None, optional): Value which will be returned if not found. Defaults to None.
            options (_type_, optional): Injector configuration. Defaults to { "optional": False }.

        Returns:
            T: An object resolved to `token`
            Any: In case if unable to resolve, token not found and `not_found_value` set to type other then `None`
            None: In case if unable to resolve dependency, token not found and `not_found_value` set to `None`
        """
        ...

    
    def get(
        self,
        token: type[T] | str | Any,
        not_found_value: Any | None = RAISE_NOT_FOUND,
        options: InjectorOptions = {
            "optional": False
        }
    ) -> T | Any | None:
        ...