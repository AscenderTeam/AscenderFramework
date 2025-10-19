from inspect import Parameter
from typing import Any, TypeVar, overload
from ascender.core.di.interface.injection_metadata import InjectionMetadata


T = TypeVar("T")


@overload
def Inject(__token: str) -> Any: ...

@overload
def Inject(__token: type[T]) -> T: ...

@overload
def Inject(__token: str, __fallback: Any) -> Any: ...

@overload
def Inject(__token: type[T], __fallback: Any) -> T: ...

def Inject(__token: type[T] | str, __fallback: Any = Parameter.empty) -> T | Any:
    return InjectionMetadata(__token, __fallback)