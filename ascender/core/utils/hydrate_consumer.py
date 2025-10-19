from typing import Any, Callable, Sequence

from ascender.core.struct.controller_ref import ControllerRef
from ascender.core.struct.module_ref import AscModuleRef
from ascender.guards.guard import Guard
from ascender.guards.paramguard import ParamGuard


""":internal:"""
def foreach_consumers(
    module: AscModuleRef,
    consumers: Sequence[type[ControllerRef | Guard | ParamGuard]], 
    fn: Callable[[type[ControllerRef | Guard | ParamGuard]], None]
):
    """
    Iterates over all declaration consumers of module.
    Applies monkey-patching on all non-controller declarations
    """
    for consumer in consumers:
        if not hasattr(consumer, "__controller__"):
            consumer.__di_module__ = module

        fn(consumer)