from typing import TypeVar, TypedDict

from ascender.core.di.interface.provider import Provider


T = TypeVar("T")


class IBootstrap(TypedDict):
    providers: list[Provider]