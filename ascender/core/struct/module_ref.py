from typing import TYPE_CHECKING, Any, MutableSequence
from ascender.core.di.injector import AscenderInjector

if TYPE_CHECKING:
    from ascender.core.struct.module import AscModule


class AscModuleRef:
    _injector: AscenderInjector | None
    _consumers: MutableSequence[Any] = []

    __asc_module__: "AscModule"