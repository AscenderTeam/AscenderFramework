from dataclasses import dataclass
from typing import Any, Callable, Literal

from ascender.abstracts.factory import AbstractFactory
from ascender.abstracts.module import AbstractModule


@dataclass
class Provider:
    injectable: type[Any | AbstractModule] | AbstractFactory
    provider_type: Literal["factory_method", "classic", "abstract_factory"] = "classic"
    factory_method: Callable[..., Any | AbstractModule] | None = None
    is_lazy: bool = False