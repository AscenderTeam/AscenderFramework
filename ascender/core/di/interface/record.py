from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar


T = TypeVar("T")


@dataclass()
class ProviderRecord(Generic[T]):
    value: T | dict | Any
    factory: Callable[[], T] | None = None
    multi: bool = False

    def __hash__(self) -> int:
        return hash((id(self.factory), self.multi))