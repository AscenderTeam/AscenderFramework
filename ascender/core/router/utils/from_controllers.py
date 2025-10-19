from typing import Sequence
from ascender.core.di.injector import AscenderInjector
from ascender.core.router.interface.route import RouterRoute
from ascender.core.router.router import RouterNode
from ascender.core.struct.controller_ref import ControllerRef
from ascender.core.struct.module_ref import AscModuleRef


""":internal:"""
def handle_module_consumers(loaded_module: type[AscModuleRef], injector: AscenderInjector) -> list[RouterNode]:
    """
    Handles all module's consumers

    Args:
        loaded_module (type[AscModuleRef]): Reference to loaded `AscModule`
    """
    asc_module = loaded_module.__asc_module__
    
    # Reset and empty all active consumers of the module to avoid duplicates
    asc_module.active_consumers = []
    
    # Collector of consumers
    graph = []

    for consumer in asc_module.consumers:
        if consumer in asc_module.exports and hasattr(consumer, "__controller__"):
            graph.append(build_router_node(consumer, loaded_module, injector))
    
    for imported_module in asc_module.imported_modules:
        if imported_module in asc_module.exports:
            if hasattr(imported_module, "__controller__"):
                graph.append(build_router_node(imported_module, None, injector))
            graph.extend(handle_module_consumers(imported_module, injector))
    
    return graph


def build_router_node(consumer: type[ControllerRef], parent_module: type[AscModuleRef] | None, injector: AscenderInjector):
    # Preparing all necessert data to build `path`, `tags` and etc
    prefix = consumer.__controller__.prefix.rstrip("/")
    pathname = consumer.__controller__.name if consumer.__controller__.name else consumer.__name__.removesuffix("Controller").lower()
    pathname = pathname.strip("/")
    suffix = consumer.__controller__.suffix.strip("/")
    tags = consumer.__controller__.tags if consumer.__controller__.tags else [consumer.__name__.removesuffix("Controller")]

    node = RouterNode({
        "path": f"{prefix}/{pathname}/{suffix}".rstrip("/"),
        "tags": tags,
        "controller": consumer,
        "load_controller": (lambda: parent_module) if parent_module else None,
        "include_in_schema": True
    }, injector=injector)

    return node