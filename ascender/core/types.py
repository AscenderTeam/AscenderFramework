from typing import TypedDict, TypeVar

from ascender.core.di.interface.provider import Provider

T = TypeVar("T")


class IBootstrap(TypedDict):
    providers: list[Provider]
