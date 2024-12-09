from abc import ABC
from dataclasses import dataclass
from typing import Any, List, NotRequired, TypeVar, TypedDict
from tortoise.models import Model as Entity

from ascender.contrib.repositories import Repository
from ascender.contrib.services import Service


T = TypeVar("T")


class Controller(ABC):
    pass


class IBootstrap(TypedDict):
    providers: list[T]