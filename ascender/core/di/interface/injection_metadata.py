from inspect import Parameter
from typing import Any, Generic, TypeVar


T = TypeVar("T")


class InjectionMetadata(Generic[T]):
    def __init__(self, token: str | type[T], fallback: Any = Parameter.empty) -> None:
        self.token = token
        self.fallback = fallback
        self.type = T
    
    def __repr__(self):
        return f"InjectionMetadata(token={self.token}, fallback={self.fallback}, type={self.type})"